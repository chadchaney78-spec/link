/**
 * LINK Studio OS - Mission Control Frontend
 * Handles navigation, data loading, and CRUD operations for Money and Social
 */

// API Configuration
const API_BASE = window.location.origin;
let studioData = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initModal();
    loadStudioData();
    initActionButtons();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item[data-view]');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewId = item.getAttribute('data-view');
            switchView(viewId);
            
            // Update active nav item
            navItems.forEach(ni => ni.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewId) {
    const views = document.querySelectorAll('.view-content');
    views.forEach(view => view.classList.remove('active'));
    
    const targetView = document.getElementById(`view-${viewId}`);
    if (targetView) {
        targetView.classList.add('active');
    }
}

// Data Loading
async function loadStudioData() {
    try {
        const response = await fetch(`${API_BASE}/api/studio-os`);
        if (!response.ok) throw new Error('Failed to load studio data');
        
        studioData = await response.json();
        console.log('Studio OS loaded:', studioData);
        
        // Render all sections
        renderInvoices(studioData.money_registers.invoices);
        renderProposals(studioData.money_registers.proposals);
        renderSocialPosts(studioData.social_media.posts);
        
    } catch (error) {
        console.error('Error loading studio data:', error);
        showError('Failed to load data. Check server connection.');
    }
}

// Invoices
function renderInvoices(invoices) {
    const tbody = document.getElementById('invoices-tbody');
    const count = document.getElementById('invoice-count');
    
    count.textContent = invoices.length;
    
    if (invoices.length === 0) {
        tbody.innerHTML = '<tr class="loading-row"><td colspan="11">No invoices yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = invoices.map(inv => `
        <tr>
            <td><code class="link-badge">${inv.invoice_id}</code></td>
            <td>${inv.proposal_id ? `<code class="link-badge">${inv.proposal_id}</code>` : '—'}</td>
            <td>${inv.job_ticket ? `<code class="link-badge">${inv.job_ticket}</code>` : '—'}</td>
            <td>${inv.client_slug || '—'}</td>
            <td class="col-number">$${parseFloat(inv.amount || 0).toLocaleString()}</td>
            <td><span class="status-badge status-${inv.status}">${inv.status}</span></td>
            <td>${inv.date_issued || '—'}</td>
            <td>${inv.date_due || '—'}</td>
            <td>${inv.date_paid || '—'}</td>
            <td class="col-notes" title="${inv.notes || ''}">${inv.notes || '—'}</td>
            <td class="col-actions">
                <button class="btn-edit" onclick="editInvoice('${inv.invoice_id}')">Edit</button>
            </td>
        </tr>
    `).join('');
}

async function saveInvoice(data) {
    try {
        const response = await fetch(`${API_BASE}/api/money/invoices`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save invoice');
        
        await loadStudioData();
        closeModal();
        showSuccess('Invoice saved successfully');
        
    } catch (error) {
        console.error('Error saving invoice:', error);
        showError('Failed to save invoice');
    }
}

function editInvoice(invoiceId) {
    const invoice = studioData.money_registers.invoices.find(i => i.invoice_id === invoiceId);
    if (!invoice) return;
    
    showModal('Edit Invoice', {
        invoice_id: {label: 'Invoice ID', value: invoice.invoice_id, readonly: true},
        proposal_id: {label: 'Proposal ID', value: invoice.proposal_id},
        job_ticket: {label: 'Job Ticket', value: invoice.job_ticket},
        client_slug: {label: 'Client Slug', value: invoice.client_slug},
        amount: {label: 'Amount', value: invoice.amount, type: 'number'},
        status: {label: 'Status', value: invoice.status, type: 'select', options: ['draft', 'sent', 'paid', 'overdue']},
        date_issued: {label: 'Date Issued', value: invoice.date_issued, type: 'date'},
        date_due: {label: 'Date Due', value: invoice.date_due, type: 'date'},
        date_paid: {label: 'Date Paid', value: invoice.date_paid, type: 'date'},
        notes: {label: 'Notes', value: invoice.notes, type: 'textarea'}
    }, (formData) => saveInvoice(formData));
}

// Proposals
function renderProposals(proposals) {
    const tbody = document.getElementById('proposals-tbody');
    const count = document.getElementById('proposal-count');
    
    count.textContent = proposals.length;
    
    if (proposals.length === 0) {
        tbody.innerHTML = '<tr class="loading-row"><td colspan="11">No proposals yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = proposals.map(prop => `
        <tr>
            <td><code class="link-badge">${prop.proposal_id}</code></td>
            <td>${prop.job_ticket ? `<code class="link-badge">${prop.job_ticket}</code>` : '—'}</td>
            <td>${prop.lead_slug || '—'}</td>
            <td>${prop.client_name || '—'}</td>
            <td class="col-number">$${parseFloat(prop.amount || 0).toLocaleString()}</td>
            <td><span class="status-badge status-${prop.status}">${prop.status}</span></td>
            <td>${prop.date_created || '—'}</td>
            <td>${prop.date_sent || '—'}</td>
            <td>${prop.date_accepted || '—'}</td>
            <td class="col-notes" title="${prop.scope_summary || ''}">${prop.scope_summary || '—'}</td>
            <td class="col-actions">
                <button class="btn-edit" onclick="editProposal('${prop.proposal_id}')">Edit</button>
            </td>
        </tr>
    `).join('');
}

async function saveProposal(data) {
    try {
        const response = await fetch(`${API_BASE}/api/money/proposals`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save proposal');
        
        await loadStudioData();
        closeModal();
        showSuccess('Proposal saved successfully');
        
    } catch (error) {
        console.error('Error saving proposal:', error);
        showError('Failed to save proposal');
    }
}

function editProposal(proposalId) {
    const proposal = studioData.money_registers.proposals.find(p => p.proposal_id === proposalId);
    if (!proposal) return;
    
    showModal('Edit Proposal', {
        proposal_id: {label: 'Proposal ID', value: proposal.proposal_id, readonly: true},
        job_ticket: {label: 'Job Ticket', value: proposal.job_ticket},
        lead_slug: {label: 'Lead Slug', value: proposal.lead_slug},
        client_name: {label: 'Client Name', value: proposal.client_name},
        amount: {label: 'Amount', value: proposal.amount, type: 'number'},
        status: {label: 'Status', value: proposal.status, type: 'select', options: ['draft', 'sent', 'accepted', 'rejected']},
        date_created: {label: 'Date Created', value: proposal.date_created, type: 'date'},
        date_sent: {label: 'Date Sent', value: proposal.date_sent, type: 'date'},
        date_accepted: {label: 'Date Accepted', value: proposal.date_accepted, type: 'date'},
        scope_summary: {label: 'Scope Summary', value: proposal.scope_summary, type: 'textarea'}
    }, (formData) => saveProposal(formData));
}

// Social Media Posts
function renderSocialPosts(posts) {
    const tbody = document.getElementById('posts-tbody');
    const count = document.getElementById('post-count');
    
    count.textContent = posts.length;
    
    if (posts.length === 0) {
        tbody.innerHTML = '<tr class="loading-row"><td colspan="10">No posts scheduled yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = posts.map(post => `
        <tr>
            <td>${post.date}</td>
            <td><span class="status-badge status-${post.channel}">${post.channel}</span></td>
            <td>${post.type}</td>
            <td class="col-notes" title="${post.hook}">${post.hook}</td>
            <td><code>${post.asset || '—'}</code></td>
            <td class="col-notes" title="${post.cta}">${post.cta || '—'}</td>
            <td><span class="status-badge status-${post.status}">${post.status}</span></td>
            <td><span class="status-badge status-${post.identity}">${post.identity}</span></td>
            <td class="col-notes" title="${post.draft_file}"><code>${post.draft_file || '—'}</code></td>
            <td class="col-actions">
                <button class="btn-edit" onclick="editPost('${post.id}')">Edit</button>
                <button class="btn-delete" onclick="deletePost('${post.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function savePost(data) {
    try {
        const response = await fetch(`${API_BASE}/api/social/posts`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Failed to save post');
        
        await loadStudioData();
        closeModal();
        showSuccess('Post saved successfully');
        
    } catch (error) {
        console.error('Error saving post:', error);
        showError('Failed to save post');
    }
}

async function deletePost(postId) {
    if (!confirm('Delete this post? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/social/posts`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: postId})
        });
        
        if (!response.ok) throw new Error('Failed to delete post');
        
        await loadStudioData();
        showSuccess('Post deleted');
        
    } catch (error) {
        console.error('Error deleting post:', error);
        showError('Failed to delete post');
    }
}

function editPost(postId) {
    const post = studioData.social_media.posts.find(p => p.id === postId);
    if (!post) return;
    
    showModal('Edit Social Post', {
        id: {label: 'Post ID', value: post.id, readonly: true},
        date: {label: 'Date', value: post.date, type: 'date'},
        channel: {label: 'Channel', value: post.channel, type: 'select', options: ['linkedin', 'twitter', 'instagram', 'facebook']},
        type: {label: 'Type', value: post.type},
        hook: {label: 'Hook', value: post.hook, type: 'textarea'},
        asset: {label: 'Asset', value: post.asset},
        cta: {label: 'CTA', value: post.cta},
        status: {label: 'Status', value: post.status, type: 'select', options: ['review', 'approved', 'scheduled', 'posted']},
        identity: {label: 'Identity', value: post.identity, type: 'select', options: ['chad', 'link']},
        draft_file: {label: 'Draft File Link', value: post.draft_file}
    }, (formData) => savePost(formData));
}

// Modal System
let currentModalSave = null;

function initModal() {
    const modal = document.getElementById('edit-modal');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('modal-cancel');
    const saveBtn = document.getElementById('modal-save');
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    saveBtn.addEventListener('click', saveModalForm);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
}

function showModal(title, fields, onSave) {
    const modal = document.getElementById('edit-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.textContent = title;
    currentModalSave = onSave;
    
    // Build form
    let formHtml = '';
    for (const [key, config] of Object.entries(fields)) {
        const type = config.type || 'text';
        const readonly = config.readonly ? 'readonly' : '';
        
        formHtml += `
            <div class="form-field">
                <label for="field-${key}">${config.label}</label>
        `;
        
        if (type === 'textarea') {
            formHtml += `<textarea id="field-${key}" ${readonly}>${config.value || ''}</textarea>`;
        } else if (type === 'select') {
            formHtml += `<select id="field-${key}" ${readonly}>`;
            config.options.forEach(opt => {
                const selected = opt === config.value ? 'selected' : '';
                formHtml += `<option value="${opt}" ${selected}>${opt}</option>`;
            });
            formHtml += `</select>`;
        } else {
            formHtml += `<input type="${type}" id="field-${key}" value="${config.value || ''}" ${readonly}>`;
        }
        
        formHtml += `</div>`;
    }
    
    modalBody.innerHTML = formHtml;
    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('edit-modal');
    modal.classList.remove('active');
    currentModalSave = null;
}

function saveModalForm() {
    const modalBody = document.getElementById('modal-body');
    const fields = modalBody.querySelectorAll('input, select, textarea');
    
    const formData = {};
    fields.forEach(field => {
        const key = field.id.replace('field-', '');
        formData[key] = field.value;
    });
    
    if (currentModalSave) {
        currentModalSave(formData);
    }
}

// Action Buttons
function initActionButtons() {
    document.getElementById('btn-new-invoice').addEventListener('click', () => {
        showModal('New Invoice', {
            invoice_id: {label: 'Invoice ID', value: '', placeholder: 'Auto-generated'},
            proposal_id: {label: 'Proposal ID', value: ''},
            job_ticket: {label: 'Job Ticket', value: ''},
            client_slug: {label: 'Client Slug', value: ''},
            amount: {label: 'Amount', value: '0', type: 'number'},
            status: {label: 'Status', value: 'draft', type: 'select', options: ['draft', 'sent', 'paid', 'overdue']},
            date_issued: {label: 'Date Issued', value: '', type: 'date'},
            date_due: {label: 'Date Due', value: '', type: 'date'},
            date_paid: {label: 'Date Paid', value: '', type: 'date'},
            notes: {label: 'Notes', value: '', type: 'textarea'}
        }, async (formData) => {
            try {
                const response = await fetch(`${API_BASE}/api/money/invoices`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to create invoice');
                
                await loadStudioData();
                closeModal();
                showSuccess('Invoice created successfully');
                
            } catch (error) {
                console.error('Error creating invoice:', error);
                showError('Failed to create invoice');
            }
        });
    });
    
    document.getElementById('btn-new-proposal').addEventListener('click', () => {
        showModal('New Proposal', {
            proposal_id: {label: 'Proposal ID', value: '', placeholder: 'Auto-generated'},
            job_ticket: {label: 'Job Ticket', value: ''},
            lead_slug: {label: 'Lead Slug', value: ''},
            client_name: {label: 'Client Name', value: ''},
            amount: {label: 'Amount', value: '0', type: 'number'},
            status: {label: 'Status', value: 'draft', type: 'select', options: ['draft', 'sent', 'accepted', 'rejected']},
            date_created: {label: 'Date Created', value: '', type: 'date'},
            date_sent: {label: 'Date Sent', value: '', type: 'date'},
            date_accepted: {label: 'Date Accepted', value: '', type: 'date'},
            scope_summary: {label: 'Scope Summary', value: '', type: 'textarea'}
        }, async (formData) => {
            try {
                const response = await fetch(`${API_BASE}/api/money/proposals`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to create proposal');
                
                await loadStudioData();
                closeModal();
                showSuccess('Proposal created successfully');
                
            } catch (error) {
                console.error('Error creating proposal:', error);
                showError('Failed to create proposal');
            }
        });
    });
    
    document.getElementById('btn-new-post').addEventListener('click', () => {
        showModal('New Social Post', {
            id: {label: 'Post ID', value: '', placeholder: 'Auto-generated'},
            date: {label: 'Date', value: '', type: 'date'},
            channel: {label: 'Channel', value: 'linkedin', type: 'select', options: ['linkedin', 'twitter', 'instagram', 'facebook']},
            type: {label: 'Type', value: ''},
            hook: {label: 'Hook', value: '', type: 'textarea'},
            asset: {label: 'Asset', value: ''},
            cta: {label: 'CTA', value: ''},
            status: {label: 'Status', value: 'review', type: 'select', options: ['review', 'approved', 'scheduled', 'posted']},
            identity: {label: 'Identity', value: 'chad', type: 'select', options: ['chad', 'link']},
            draft_file: {label: 'Draft File Link', value: ''}
        }, async (formData) => {
            try {
                const response = await fetch(`${API_BASE}/api/social/posts`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to create post');
                
                await loadStudioData();
                closeModal();
                showSuccess('Post created successfully');
                
            } catch (error) {
                console.error('Error creating post:', error);
                showError('Failed to create post');
            }
        });
    });
}

// Notifications
function showSuccess(message) {
    console.log('✅', message);
    // Could add toast notification UI here
}

function showError(message) {
    console.error('❌', message);
    alert(message);
}

// Make functions globally available for inline onclick handlers
window.editInvoice = editInvoice;
window.editProposal = editProposal;
window.editPost = editPost;
window.deletePost = deletePost;
