"""
Tests for LINK Studio OS backend
"""

import os
import sys
import json
import csv
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import studio_os
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from studio_os import app, read_csv_register, write_csv_register, read_json_data, write_json_data
from studio_os import INVOICE_FIELDS, PROPOSAL_FIELDS


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with test data"""
    # Create directory structure
    money_invoices = tmp_path / 'Company' / 'Money' / 'Invoices'
    money_proposals = tmp_path / 'Company' / 'Money' / 'Proposals'
    social = tmp_path / 'Company' / 'Marketing' / 'social'
    ops = tmp_path / 'Company' / 'Ops' / 'Studio'
    
    money_invoices.mkdir(parents=True)
    money_proposals.mkdir(parents=True)
    social.mkdir(parents=True)
    ops.mkdir(parents=True)
    
    # Create test CSV data
    invoices_csv = money_invoices / 'register.csv'
    with open(invoices_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=INVOICE_FIELDS)
        writer.writeheader()
        writer.writerow({
            'invoice_id': 'INV-TEST-001',
            'proposal_id': 'PROP-TEST-001',
            'job_ticket': 'TICKET-001',
            'client_slug': 'test-client',
            'amount': '1000.00',
            'status': 'draft',
            'date_issued': '2026-09-01',
            'date_due': '2026-09-15',
            'date_paid': '',
            'notes': 'Test invoice'
        })
    
    proposals_csv = money_proposals / 'register.csv'
    with open(proposals_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=PROPOSAL_FIELDS)
        writer.writeheader()
        writer.writerow({
            'proposal_id': 'PROP-TEST-001',
            'job_ticket': 'TICKET-001',
            'lead_slug': 'test-client',
            'client_name': 'Test Client Inc',
            'amount': '2000.00',
            'status': 'sent',
            'date_created': '2026-08-01',
            'date_sent': '2026-08-02',
            'date_accepted': '',
            'scope_summary': 'Test project scope'
        })
    
    # Create test JSON data
    social_json = social / 'studio-social.json'
    with open(social_json, 'w') as f:
        json.dump({
            'revision': '2026-09-20T00:00:00Z',
            'posts': [
                {
                    'id': 'post-test-001',
                    'date': '2026-09-25',
                    'channel': 'linkedin',
                    'type': 'test',
                    'hook': 'Test post hook',
                    'asset': 'test.png',
                    'cta': 'Test CTA',
                    'status': 'review',
                    'identity': 'chad',
                    'draft_file': 'test.md'
                }
            ]
        }, f)
    
    ops_json = ops / 'records.json'
    with open(ops_json, 'w') as f:
        json.dump({
            'revision': '2026-09-20T00:00:00Z',
            'events': [],
            'notes': [],
            'channels': []
        }, f)
    
    return tmp_path


def test_read_csv_register(temp_workspace):
    """Test CSV reading"""
    csv_path = temp_workspace / 'Company' / 'Money' / 'Invoices' / 'register.csv'
    rows = read_csv_register(str(csv_path), INVOICE_FIELDS)
    
    assert len(rows) == 1
    assert rows[0]['invoice_id'] == 'INV-TEST-001'
    assert rows[0]['amount'] == '1000.00'


def test_write_csv_register(temp_workspace):
    """Test CSV writing with backup"""
    csv_path = temp_workspace / 'Company' / 'Money' / 'Invoices' / 'register.csv'
    
    # Read existing
    rows = read_csv_register(str(csv_path), INVOICE_FIELDS)
    
    # Modify
    rows[0]['amount'] = '1500.00'
    rows.append({
        'invoice_id': 'INV-TEST-002',
        'proposal_id': '',
        'job_ticket': '',
        'client_slug': 'another-client',
        'amount': '500.00',
        'status': 'paid',
        'date_issued': '2026-09-10',
        'date_due': '2026-09-20',
        'date_paid': '2026-09-19',
        'notes': 'Another test'
    })
    
    # Write
    write_csv_register(str(csv_path), INVOICE_FIELDS, rows)
    
    # Verify backup created
    backup_path = csv_path.with_suffix('.csv.bak')
    assert backup_path.exists()
    
    # Verify new data
    new_rows = read_csv_register(str(csv_path), INVOICE_FIELDS)
    assert len(new_rows) == 2
    assert new_rows[0]['amount'] == '1500.00'
    assert new_rows[1]['invoice_id'] == 'INV-TEST-002'


def test_read_json_data(temp_workspace):
    """Test JSON reading"""
    json_path = temp_workspace / 'Company' / 'Marketing' / 'social' / 'studio-social.json'
    data = read_json_data(str(json_path))
    
    assert 'posts' in data
    assert len(data['posts']) == 1
    assert data['posts'][0]['id'] == 'post-test-001'


def test_write_json_data(temp_workspace):
    """Test JSON writing with revision update"""
    json_path = temp_workspace / 'Company' / 'Marketing' / 'social' / 'studio-social.json'
    
    # Read existing
    data = read_json_data(str(json_path))
    original_revision = data['revision']
    
    # Modify
    data['posts'].append({
        'id': 'post-test-002',
        'date': '2026-09-26',
        'channel': 'twitter',
        'type': 'test',
        'hook': 'Another test',
        'asset': '',
        'cta': '',
        'status': 'draft',
        'identity': 'link',
        'draft_file': ''
    })
    
    # Write
    write_json_data(str(json_path), data)
    
    # Verify backup created
    backup_path = json_path.with_suffix('.json.bak')
    assert backup_path.exists()
    
    # Verify new data
    new_data = read_json_data(str(json_path))
    assert len(new_data['posts']) == 2
    assert new_data['revision'] != original_revision  # Revision should be updated


def test_api_health(client):
    """Test health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'paths' in data


def test_api_studio_os_payload(client, monkeypatch, temp_workspace):
    """Test main studio OS payload endpoint"""
    # Monkeypatch resolve_path to use temp workspace
    import studio_os
    
    def mock_resolve_path(rel_path):
        return temp_workspace / rel_path
    
    monkeypatch.setattr(studio_os, 'resolve_path', mock_resolve_path)
    
    response = client.get('/api/studio-os')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'money_registers' in data
    assert 'social_media' in data
    assert 'ops_records' in data
    
    # Check money data
    assert len(data['money_registers']['invoices']) == 1
    assert len(data['money_registers']['proposals']) == 1
    
    # Check linkage
    linkage = data['money_registers']['linkage']
    assert 'TICKET-001' in linkage
    assert 'PROP-TEST-001' in linkage['TICKET-001']['proposals']
    assert 'INV-TEST-001' in linkage['TICKET-001']['invoices']
    
    # Check social data
    assert len(data['social_media']['posts']) == 1


def test_invoice_fields_complete():
    """Verify invoice fields are complete"""
    expected_fields = [
        'invoice_id', 'proposal_id', 'job_ticket', 'client_slug',
        'amount', 'status', 'date_issued', 'date_due', 'date_paid', 'notes'
    ]
    assert INVOICE_FIELDS == expected_fields


def test_proposal_fields_complete():
    """Verify proposal fields are complete"""
    expected_fields = [
        'proposal_id', 'job_ticket', 'lead_slug', 'client_name',
        'amount', 'status', 'date_created', 'date_sent', 'date_accepted', 'scope_summary'
    ]
    assert PROPOSAL_FIELDS == expected_fields


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
