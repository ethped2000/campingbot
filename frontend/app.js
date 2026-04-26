const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    loadCampgrounds();
    loadSearches();

    document.getElementById('searchForm').addEventListener('submit', handleAddSearch);
});

// Save searches to localStorage for persistence
function saveSearchesToMemory(searches) {
    try {
        localStorage.setItem('campingbot_searches', JSON.stringify(searches));
    } catch (e) {
        console.warn('Could not save to localStorage:', e);
    }
}

// Load searches from localStorage if available
function getSearchesFromMemory() {
    try {
        const cached = localStorage.getItem('campingbot_searches');
        return cached ? JSON.parse(cached) : null;
    } catch (e) {
        console.warn('Could not load from localStorage:', e);
        return null;
    }
}

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
        console.log('Loading searches from API...');
        const response = await fetch(`${API_BASE}/searches/`);

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const searches = await response.json();
        console.log(`Found ${searches.length} searches in database`);

        // Save to localStorage for persistence
        saveSearchesToMemory(searches);

        const searchesList = document.getElementById('searchesList');

        if (searches.length === 0) {
            const cached = getSearchesFromMemory();
            if (cached && cached.length > 0) {
                console.log('Database empty but found cached searches in localStorage');
            } else {
                searchesList.innerHTML = '<p class="empty-state">No searches yet. Add one above!</p>';
                return;
            }
        }

        searchesList.innerHTML = '';

        for (const search of searches) {
            const campground = await getCampgroundName(search.campground_id);
            const card = createSearchCard(search, campground);
            searchesList.appendChild(card);
        }
    } catch (error) {
        console.error('Error loading searches from API:', error);

        // If API fails, try to use cached searches from localStorage
        const cachedSearches = getSearchesFromMemory();
        if (cachedSearches && cachedSearches.length > 0) {
            console.log(`Using ${cachedSearches.length} cached searches from localStorage`);
            const searchesList = document.getElementById('searchesList');
            searchesList.innerHTML = '';

            for (const search of cachedSearches) {
                const campground = await getCampgroundName(search.campground_id);
                const card = createSearchCard(search, campground);
                searchesList.appendChild(card);
            }
        } else {
            console.warn('No searches found in API or localStorage');
            document.getElementById('searchesList').innerHTML = '<p class="empty-state">Could not load searches. Check console.</p>';
        }
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
                <button class="btn btn-primary" onclick="scanNow(${search.id})" style="padding: 8px 12px; font-size: 0.9em; margin-right: 5px;">Scan Now</button>
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

        const availableSites = availability.filter(item => item.available);
        const unavailableSites = availability.filter(item => !item.available);

        let html = '';

        if (availableSites.length > 0) {
            html += '<div style="margin-bottom: 15px;"><strong style="color: #28a745;">✓ Available for your dates:</strong>';
            html += availableSites.map(item => `
                <div class="availability-item" style="background: #d4edda; border-left: 4px solid #28a745;">
                    <strong>${item.site_name || 'Site ' + item.site_id}</strong>
                </div>
            `).join('');
            html += '</div>';
        }

        if (unavailableSites.length > 0) {
            html += '<div><strong style="color: #dc3545;">✗ Not available:</strong>';
            html += unavailableSites.map(item => `
                <div class="availability-item" style="background: #f8d7da; border-left: 4px solid #dc3545; opacity: 0.7;">
                    <strong>${item.site_name || 'Site ' + item.site_id}</strong>
                </div>
            `).join('');
            html += '</div>';
        }

        container.innerHTML = html || '<p style="color: #999;">No sites found for these dates.</p>';
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
        showMessage('Please fill in all required fields', 'error');
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
            showMessage('Search added successfully!', 'success');
            await loadSearches();
        } else {
            const errorData = await response.json();
            showMessage('Error adding search: ' + (errorData.detail || 'Unknown error'), 'error');
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
            showMessage('Search deleted successfully!', 'success');
            await loadSearches();
        } else {
            const errorData = await response.json();
            showMessage('Error deleting search: ' + (errorData.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error deleting search:', error);
        showMessage('Error deleting search: ' + error.message, 'error');
    }
}

async function scanNow(searchId) {
    try {
        showMessage('Scanning for availability...', 'success');

        const response = await fetch('/api/scraper/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            await new Promise(resolve => setTimeout(resolve, 2000));
            loadAvailability(searchId);
            showMessage('Scan complete! Availability updated.', 'success');
        } else {
            showMessage('Error scanning availability', 'error');
        }
    } catch (error) {
        console.error('Error scanning:', error);
        showMessage('Error scanning: ' + error.message, 'error');
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
