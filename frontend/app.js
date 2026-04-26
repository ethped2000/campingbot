const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    loadCampgrounds();
    loadSearches();

    document.getElementById('searchForm').addEventListener('submit', handleAddSearch);
});

async function loadCampgrounds() {
    try {
        const response = await fetch(`${API_BASE}/campgrounds/`);
        const campgrounds = await response.json();

        const campgroundSelect = document.getElementById('campground');
        campgroundSelect.innerHTML = '';

        if (campgrounds.length === 0) {
            campgroundSelect.innerHTML = '<option value="">No campgrounds available</option>';
            return;
        }

        campgrounds.forEach(cg => {
            const option = document.createElement('option');
            option.value = cg.id;
            option.textContent = cg.name + (cg.region ? ` (${cg.region})` : '');
            campgroundSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading campgrounds:', error);
        document.getElementById('campground').innerHTML = '<option value="">Error loading campgrounds</option>';
    }
}

async function loadSearches() {
    try {
        const response = await fetch(`${API_BASE}/searches/`);
        const searches = await response.json();

        const searchesList = document.getElementById('searchesList');

        if (searches.length === 0) {
            searchesList.innerHTML = '<p class="empty-state">No searches yet. Add one above!</p>';
            return;
        }

        searchesList.innerHTML = '';

        for (const search of searches) {
            const campground = await getCampgroundName(search.campground_id);
            const card = createSearchCard(search, campground);
            searchesList.appendChild(card);
        }
    } catch (error) {
        console.error('Error loading searches:', error);
    }
}

async function getCampgroundName(campgroundId) {
    try {
        const response = await fetch(`${API_BASE}/campgrounds/`);
        const campgrounds = await response.json();
        const cg = campgrounds.find(c => c.id === campgroundId);
        return cg ? cg.name : 'Unknown Campground';
    } catch {
        return 'Unknown Campground';
    }
}

function createSearchCard(search, campgroundName) {
    const card = document.createElement('div');
    card.className = 'search-card';

    const checkInDate = new Date(search.check_in_date).toLocaleDateString();
    const checkOutDate = new Date(search.check_out_date).toLocaleDateString();

    card.innerHTML = `
        <div class="search-header">
            <div class="search-title">${campgroundName}</div>
            <div>
                <span class="search-status status-active">${search.status}</span>
                <button class="btn btn-danger" onclick="deleteSearch(${search.id})">Delete</button>
            </div>
        </div>
        <div class="search-details">
            <div class="detail-item">
                <div class="detail-label">Check-in</div>
                <div class="detail-value">${checkInDate}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Check-out</div>
                <div class="detail-value">${checkOutDate}</div>
            </div>
            ${search.site_type ? `
                <div class="detail-item">
                    <div class="detail-label">Site Type</div>
                    <div class="detail-value">${search.site_type}</div>
                </div>
            ` : ''}
        </div>
        <div class="availability-section">
            <strong>Availability:</strong>
            <div class="availability-list" id="availability-${search.id}">
                <div class="loading"></div> Loading...
            </div>
        </div>
    `;

    loadAvailability(search.id);
    return card;
}

async function loadAvailability(searchId) {
    try {
        const response = await fetch(`${API_BASE}/searches/${searchId}/availability`);
        const availability = await response.json();

        const container = document.getElementById(`availability-${searchId}`);

        if (availability.length === 0) {
            container.innerHTML = '<p style="font-size: 0.9em; color: #999;">No availability data yet</p>';
            return;
        }

        container.innerHTML = availability.map(item => `
            <div class="availability-item">
                <div>
                    <strong>${item.site_name || 'Site ' + item.site_id}</strong>
                    ${item.date ? ` - ${new Date(item.date).toLocaleDateString()}` : ''}
                </div>
                <span class="${item.available ? 'available' : 'unavailable'}">
                    ${item.available ? '✓ Available' : '✗ Not Available'}
                </span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading availability:', error);
        const container = document.getElementById(`availability-${searchId}`);
        container.innerHTML = '<p style="color: #ff6b6b;">Error loading availability</p>';
    }
}

async function handleAddSearch(e) {
    e.preventDefault();

    const campgroundId = document.getElementById('campground').value;
    const siteType = document.getElementById('siteType').value;
    const checkInDate = document.getElementById('checkInDate').value;
    const checkOutDate = document.getElementById('checkOutDate').value;

    if (!campgroundId || !checkInDate || !checkOutDate) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/searches/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                campground_id: parseInt(campgroundId),
                site_type: siteType || null,
                check_in_date: checkInDate,
                check_out_date: checkOutDate
            })
        });

        if (response.ok) {
            document.getElementById('searchForm').reset();
            loadSearches();
            showMessage('Search added successfully!', 'success');
        } else {
            showMessage('Error adding search', 'error');
        }
    } catch (error) {
        console.error('Error adding search:', error);
        showMessage('Error adding search: ' + error.message, 'error');
    }
}

async function deleteSearch(searchId) {
    if (!confirm('Are you sure you want to delete this search?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/searches/${searchId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadSearches();
            showMessage('Search deleted successfully!', 'success');
        } else {
            showMessage('Error deleting search', 'error');
        }
    } catch (error) {
        console.error('Error deleting search:', error);
        showMessage('Error deleting search', 'error');
    }
}

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = type;
    messageDiv.textContent = message;
    messageDiv.style.position = 'fixed';
    messageDiv.style.top = '20px';
    messageDiv.style.right = '20px';
    messageDiv.style.zIndex = '1000';
    messageDiv.style.maxWidth = '400px';

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}
