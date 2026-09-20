#!/usr/bin/env python3
"""
LINK Studio OS - Mission Control Backend
Serves Money (invoices/proposals) and Social Media data with CRUD operations.
"""

import os
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path resolution - support both local Mac path and repo structure
WORKSPACE = Path(__file__).resolve().parents[4]  # Up to /workspace
LOCAL_MAC = Path('/Users/chane/Desktop/MyLINK')

def resolve_path(rel_path):
    """Try local Mac path first, fall back to repo structure"""
    mac_path = LOCAL_MAC / rel_path
    if mac_path.exists():
        return mac_path
    return WORKSPACE / rel_path

# CSV field definitions
INVOICE_FIELDS = [
    'invoice_id', 'proposal_id', 'job_ticket', 'client_slug', 
    'amount', 'status', 'date_issued', 'date_due', 'date_paid', 'notes'
]

PROPOSAL_FIELDS = [
    'proposal_id', 'job_ticket', 'lead_slug', 'client_name',
    'amount', 'status', 'date_created', 'date_sent', 'date_accepted', 'scope_summary'
]

# Data paths
INVOICES_CSV = 'Company/Money/Invoices/register.csv'
PROPOSALS_CSV = 'Company/Money/Proposals/register.csv'
SOCIAL_JSON = 'Company/Marketing/social/studio-social.json'
OPS_RECORDS_JSON = 'Company/Ops/Studio/records.json'


def read_csv_register(csv_path, fields):
    """Read CSV register and return list of dicts"""
    path = resolve_path(csv_path)
    if not path.exists():
        return []
    
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_csv_register(csv_path, fields, rows, backup=True):
    """Write CSV register with atomic backup"""
    path = resolve_path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing
    if backup and path.exists():
        backup_path = path.with_suffix('.csv.bak')
        shutil.copy2(path, backup_path)
    
    # Write atomically
    temp_path = path.with_suffix('.csv.tmp')
    with open(temp_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    
    temp_path.replace(path)
    return True


def read_json_data(json_path):
    """Read JSON data file"""
    path = resolve_path(json_path)
    if not path.exists():
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_data(json_path, data, backup=True):
    """Write JSON data file with atomic backup"""
    path = resolve_path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing
    if backup and path.exists():
        backup_path = path.with_suffix('.json.bak')
        shutil.copy2(path, backup_path)
    
    # Write atomically with timestamp
    data['revision'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    temp_path = path.with_suffix('.json.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    temp_path.replace(path)
    return True


@app.route('/')
def index():
    """Serve the Mission Control dashboard"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static assets"""
    return send_from_directory('.', path)


@app.route('/api/studio-os')
def studio_os_payload():
    """Main Studio OS payload - all data for dashboard"""
    invoices = read_csv_register(INVOICES_CSV, INVOICE_FIELDS)
    proposals = read_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS)
    social = read_json_data(SOCIAL_JSON)
    ops = read_json_data(OPS_RECORDS_JSON)
    
    # Build ticket/proposal/invoice linkage map
    linkage = {}
    for inv in invoices:
        ticket = inv.get('job_ticket', '')
        prop = inv.get('proposal_id', '')
        if ticket:
            if ticket not in linkage:
                linkage[ticket] = {'proposals': set(), 'invoices': set()}
            linkage[ticket]['invoices'].add(inv['invoice_id'])
        if prop:
            if ticket not in linkage:
                linkage[ticket] = {'proposals': set(), 'invoices': set()}
            linkage[ticket]['proposals'].add(prop)
    
    # Convert sets to lists for JSON
    for ticket in linkage:
        linkage[ticket]['proposals'] = list(linkage[ticket]['proposals'])
        linkage[ticket]['invoices'] = list(linkage[ticket]['invoices'])
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'money_registers': {
            'invoices': invoices,
            'proposals': proposals,
            'linkage': linkage
        },
        'social_media': social,
        'ops_records': ops
    })


@app.route('/api/money/invoices', methods=['GET', 'POST', 'PUT'])
def money_invoices():
    """CRUD for invoices"""
    if request.method == 'GET':
        invoices = read_csv_register(INVOICES_CSV, INVOICE_FIELDS)
        return jsonify({'invoices': invoices})
    
    elif request.method == 'POST':
        # Create new invoice
        data = request.json
        invoices = read_csv_register(INVOICES_CSV, INVOICE_FIELDS)
        
        # Generate ID if not provided
        if not data.get('invoice_id'):
            year = datetime.now().year
            next_num = len([i for i in invoices if i['invoice_id'].startswith(f'INV-{year}')]) + 1
            data['invoice_id'] = f'INV-{year}-{next_num:03d}'
        
        invoices.append(data)
        write_csv_register(INVOICES_CSV, INVOICE_FIELDS, invoices)
        return jsonify({'status': 'created', 'invoice': data})
    
    elif request.method == 'PUT':
        # Update existing invoice
        data = request.json
        invoice_id = data.get('invoice_id')
        if not invoice_id:
            return jsonify({'error': 'invoice_id required'}), 400
        
        invoices = read_csv_register(INVOICES_CSV, INVOICE_FIELDS)
        updated = False
        for i, inv in enumerate(invoices):
            if inv['invoice_id'] == invoice_id:
                invoices[i] = data
                updated = True
                break
        
        if not updated:
            return jsonify({'error': 'invoice not found'}), 404
        
        write_csv_register(INVOICES_CSV, INVOICE_FIELDS, invoices)
        return jsonify({'status': 'updated', 'invoice': data})


@app.route('/api/money/proposals', methods=['GET', 'POST', 'PUT'])
def money_proposals():
    """CRUD for proposals"""
    if request.method == 'GET':
        proposals = read_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS)
        return jsonify({'proposals': proposals})
    
    elif request.method == 'POST':
        # Create new proposal
        data = request.json
        proposals = read_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS)
        
        # Generate ID if not provided
        if not data.get('proposal_id'):
            year = datetime.now().year
            lead_slug = data.get('lead_slug', 'XXX')[:3].upper()
            next_num = len([p for p in proposals if p['proposal_id'].startswith(f'PROP-{year}')]) + 1
            data['proposal_id'] = f'PROP-{year}-{lead_slug}-{next_num:03d}'
        
        proposals.append(data)
        write_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS, proposals)
        return jsonify({'status': 'created', 'proposal': data})
    
    elif request.method == 'PUT':
        # Update existing proposal
        data = request.json
        proposal_id = data.get('proposal_id')
        if not proposal_id:
            return jsonify({'error': 'proposal_id required'}), 400
        
        proposals = read_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS)
        updated = False
        for i, prop in enumerate(proposals):
            if prop['proposal_id'] == proposal_id:
                proposals[i] = data
                updated = True
                break
        
        if not updated:
            return jsonify({'error': 'proposal not found'}), 404
        
        write_csv_register(PROPOSALS_CSV, PROPOSAL_FIELDS, proposals)
        return jsonify({'status': 'updated', 'proposal': data})


@app.route('/api/social/posts', methods=['GET', 'POST', 'PUT', 'DELETE'])
def social_posts():
    """CRUD for social media posts"""
    if request.method == 'GET':
        social = read_json_data(SOCIAL_JSON)
        return jsonify({'posts': social.get('posts', [])})
    
    elif request.method == 'POST':
        # Create new post
        data = request.json
        social = read_json_data(SOCIAL_JSON)
        
        # Generate ID if not provided
        if not data.get('id'):
            existing_ids = [p['id'] for p in social.get('posts', [])]
            next_num = len(existing_ids) + 1
            data['id'] = f'post-{next_num:03d}'
        
        if 'posts' not in social:
            social['posts'] = []
        social['posts'].append(data)
        
        write_json_data(SOCIAL_JSON, social)
        return jsonify({'status': 'created', 'post': data})
    
    elif request.method == 'PUT':
        # Update existing post
        data = request.json
        post_id = data.get('id')
        if not post_id:
            return jsonify({'error': 'id required'}), 400
        
        social = read_json_data(SOCIAL_JSON)
        updated = False
        for i, post in enumerate(social.get('posts', [])):
            if post['id'] == post_id:
                social['posts'][i] = data
                updated = True
                break
        
        if not updated:
            return jsonify({'error': 'post not found'}), 404
        
        write_json_data(SOCIAL_JSON, social)
        return jsonify({'status': 'updated', 'post': data})
    
    elif request.method == 'DELETE':
        # Delete post
        post_id = request.json.get('id')
        if not post_id:
            return jsonify({'error': 'id required'}), 400
        
        social = read_json_data(SOCIAL_JSON)
        original_count = len(social.get('posts', []))
        social['posts'] = [p for p in social.get('posts', []) if p['id'] != post_id]
        
        if len(social['posts']) == original_count:
            return jsonify({'error': 'post not found'}), 404
        
        write_json_data(SOCIAL_JSON, social)
        return jsonify({'status': 'deleted', 'id': post_id})


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'paths': {
            'invoices': str(resolve_path(INVOICES_CSV)),
            'proposals': str(resolve_path(PROPOSALS_CSV)),
            'social': str(resolve_path(SOCIAL_JSON))
        }
    })


if __name__ == '__main__':
    print("🎯 LINK Studio OS - Mission Control")
    print(f"📁 Workspace: {WORKSPACE}")
    print(f"💰 Money: {resolve_path(INVOICES_CSV).parent}")
    print(f"📱 Social: {resolve_path(SOCIAL_JSON).parent}")
    print("🚀 Starting server on http://localhost:8792")
    app.run(host='0.0.0.0', port=8792, debug=True)
