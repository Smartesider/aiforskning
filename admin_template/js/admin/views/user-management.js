/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const userManagementView = {
    // API-endepunkter
    endpoints: {
        users: 'admin/users',
        user: 'admin/users/:id',
        roles: 'admin/roles'
    },
    
    // Lagre aktiv bruker som redigeres
    activeUser: null,
    
    // Alle tilgjengelige roller
    availableRoles: [],
    
    // Bruker-tabell element
    userTable: null,
    
    // Generer brukeradministrasjon-skjerm
    render: async function() {
        const container = document.createElement('div');
        container.className = 'user-management-container';
        
        // Opprett header
        const header = document.createElement('div');
        header.className = 'page-header';
        header.innerHTML = `
            <h1>Brukeradministrasjon</h1>
            <div class="header-actions">
                <button id="create-user-btn" class="btn primary">Opprett ny bruker</button>
            </div>
        `;
        container.appendChild(header);
        
        // Opprett søkefelt
        const searchBox = document.createElement('div');
        searchBox.className = 'search-box';
        searchBox.innerHTML = `
            <input type="text" id="user-search" placeholder="Søk etter brukere...">
            <button id="search-btn" class="btn">Søk</button>
        `;
        container.appendChild(searchBox);
        
        // Opprett brukertabell
        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-container';
        tableContainer.innerHTML = `
            <table id="user-table" class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Brukernavn</th>
                        <th>Navn</th>
                        <th>E-post</th>
                        <th>Roller</th>
                        <th>Status</th>
                        <th>Handlinger</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="7" class="loading-cell">Laster brukere...</td>
                    </tr>
                </tbody>
            </table>
        `;
        container.appendChild(tableContainer);
        
        // Opprett brukermodalvindu (skjult ved start)
        const userModal = document.createElement('div');
        userModal.id = 'user-modal';
        userModal.className = 'modal';
        userModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title">Rediger bruker</h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <form id="user-form">
                        <input type="hidden" id="user-id">
                        
                        <div class="form-group">
                            <label for="username">Brukernavn</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="full-name">Fullt navn</label>
                            <input type="text" id="full-name" name="full_name">
                        </div>
                        
                        <div class="form-group">
                            <label for="email">E-post</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Passord</label>
                            <input type="password" id="password" name="password" placeholder="La stå tomt for å beholde eksisterende">
                            <small class="form-help">Minimum 8 tegn, må inneholde tall og spesialtegn</small>
                        </div>
                        
                        <div class="form-group">
                            <label>Roller</label>
                            <div id="roles-container" class="roles-container">
                                <!-- Roller vil bli lagt til her dynamisk -->
                                <div class="loading-indicator">Laster roller...</div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="status">Status</label>
                            <select id="status" name="status">
                                <option value="active">Aktiv</option>
                                <option value="inactive">Inaktiv</option>
                                <option value="locked">Låst</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button id="save-user-btn" class="btn primary">Lagre</button>
                    <button id="cancel-user-btn" class="btn">Avbryt</button>
                </div>
            </div>
        `;
        container.appendChild(userModal);
        
        // Opprett bekreftelsesmodalvindu
        const confirmModal = document.createElement('div');
        confirmModal.id = 'confirm-modal';
        confirmModal.className = 'modal';
        confirmModal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Bekreft handling</h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <p id="confirm-message">Er du sikker på at du vil utføre denne handlingen?</p>
                </div>
                <div class="modal-footer">
                    <button id="confirm-yes-btn" class="btn danger">Ja</button>
                    <button id="confirm-no-btn" class="btn">Nei</button>
                </div>
            </div>
        `;
        container.appendChild(confirmModal);
        
        return container;
    },
    
    // Initialiser brukeradministrasjon-visning
    init: async function() {
        try {
            // Hent brukerdata
            await this.loadUsers();
            
            // Hent roller
            await this.loadRoles();
            
            // Sett opp event handlers
            this.setupEventHandlers();
        } catch (error) {
            console.error('Feil ved initialisering av brukeradministrasjon:', error);
            ui.showNotification('Kunne ikke laste brukerdata: ' + error.message, 'error');
        }
    },
    
    // Last inn brukere
    loadUsers: async function(searchTerm = '') {
        try {
            // Bygg API-endepunkt
            let endpoint = this.endpoints.users;
            if (searchTerm) {
                endpoint += `?q=${encodeURIComponent(searchTerm)}`;
            }
            
            // Hent brukere fra API
            const users = await api.get(endpoint);
            
            // Oppdater brukertabell
            const tbody = document.querySelector('#user-table tbody');
            if (!tbody) return;
            
            if (users?.length > 0) {
                // Bygg tabellrader
                let html = '';
                
                users.forEach(user => {
                    // Formater roller som kommaseparert liste
                    const roles = user.roles?.join(', ') || '';
                    
                    // Bestem statusklass basert på brukerens status
                    let statusClass = 'status-active';
                    if (user.status === 'inactive') statusClass = 'status-inactive';
                    if (user.status === 'locked') statusClass = 'status-locked';
                    
                    html += `
                        <tr data-id="${user.id}">
                            <td>${user.id}</td>
                            <td>${user.username}</td>
                            <td>${user.full_name || ''}</td>
                            <td>${user.email}</td>
                            <td>${roles}</td>
                            <td><span class="status-badge ${statusClass}">${user.status}</span></td>
                            <td class="actions-cell">
                                <button class="btn icon edit-user" title="Rediger"><i class="fas fa-edit"></i></button>
                                <button class="btn icon delete-user" title="Slett"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                });
                
                tbody.innerHTML = html;
            } else {
                // Ingen brukere funnet
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="no-results">Ingen brukere funnet</td>
                    </tr>
                `;
            }
            
            // Lagre referanse til tabellen
            this.userTable = document.getElementById('user-table');
        } catch (error) {
            console.error('Feil ved lasting av brukere:', error);
            const tbody = document.querySelector('#user-table tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="error-cell">Kunne ikke laste brukere: ${error.message}</td>
                    </tr>
                `;
            }
        }
    },
    
    // Last inn roller
    loadRoles: async function() {
        try {
            // Hent roller fra API
            const roles = await api.get(this.endpoints.roles);
            
            // Lagre roller for senere bruk
            this.availableRoles = roles || [];
        } catch (error) {
            console.error('Feil ved lasting av roller:', error);
            ui.showNotification('Kunne ikke laste brukerroller: ' + error.message, 'error');
        }
    },
    
    // Sett opp event handlers
    setupEventHandlers: function() {
        // Søk etter brukere
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('user-search');
        
        if (searchBtn && searchInput) {
            // Søk ved klikk på søkeknapp
            searchBtn.addEventListener('click', () => {
                this.loadUsers(searchInput.value);
            });
            
            // Søk ved Enter-trykk
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.loadUsers(searchInput.value);
                }
            });
        }
        
        // Opprett ny bruker
        const createBtn = document.getElementById('create-user-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.showUserModal();
            });
        }
        
        // Brukerhandlinger (rediger/slett)
        if (this.userTable) {
            this.userTable.addEventListener('click', async (e) => {
                const target = e.target.closest('button');
                if (!target) return;
                
                const row = target.closest('tr');
                const userId = row?.dataset.id;
                
                if (!userId) return;
                
                if (target.classList.contains('edit-user') || target.querySelector('.fa-edit')) {
                    // Rediger bruker
                    await this.showUserModal(userId);
                } else if (target.classList.contains('delete-user') || target.querySelector('.fa-trash')) {
                    // Slett bruker
                    this.showDeleteConfirmation(userId);
                }
            });
        }
        
        // Lagre bruker
        const saveBtn = document.getElementById('save-user-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveUser();
            });
        }
        
        // Lukk modaler
        document.querySelectorAll('.close-modal, #cancel-user-btn').forEach(el => {
            el.addEventListener('click', () => {
                this.closeModals();
            });
        });
        
        // Bekreftelsesmodal-knapper
        const confirmYesBtn = document.getElementById('confirm-yes-btn');
        const confirmNoBtn = document.getElementById('confirm-no-btn');
        
        if (confirmYesBtn) {
            confirmYesBtn.addEventListener('click', () => {
                // Utfør sletteoperasjon og lukk modal
                if (this.userToDelete) {
                    this.deleteUser(this.userToDelete);
                }
                this.closeModals();
            });
        }
        
        if (confirmNoBtn) {
            confirmNoBtn.addEventListener('click', () => {
                // Bare lukk modal
                this.closeModals();
            });
        }
        
        // Lukk modaler hvis man klikker utenfor
        window.addEventListener('click', (e) => {
            const userModal = document.getElementById('user-modal');
            const confirmModal = document.getElementById('confirm-modal');
            
            if (e.target === userModal || e.target === confirmModal) {
                this.closeModals();
            }
        });
    },
    
    // Vis brukermodal for å opprette eller redigere en bruker
    showUserModal: async function(userId = null) {
        const modal = document.getElementById('user-modal');
        const modalTitle = document.getElementById('modal-title');
        const form = document.getElementById('user-form');
        
        if (!modal || !modalTitle || !form) return;
        
        // Nullstill form
        form.reset();
        
        // Sett tittel basert på om vi oppretter eller redigerer
        modalTitle.textContent = userId ? 'Rediger bruker' : 'Opprett ny bruker';
        
        // Fyll inn roller
        await this.populateRoles();
        
        if (userId) {
            // Redigering: Hent brukerdata
            try {
                ui.showLoading(true);
                
                const endpoint = this.endpoints.user.replace(':id', userId);
                const user = await api.get(endpoint);
                
                // Lagre aktiv bruker
                this.activeUser = user;
                
                // Fyll inn skjema med brukerdata
                document.getElementById('user-id').value = user.id;
                document.getElementById('username').value = user.username;
                document.getElementById('full-name').value = user.full_name || '';
                document.getElementById('email').value = user.email;
                document.getElementById('status').value = user.status;
                
                // Merk av brukerens roller
                if (user.roles && user.roles.length > 0) {
                    user.roles.forEach(role => {
                        const checkbox = document.querySelector(`input[name="roles"][value="${role}"]`);
                        if (checkbox) {
                            checkbox.checked = true;
                        }
                    });
                }
                
                // Passordfeltet er tomt ved redigering
                document.getElementById('password').value = '';
                
                ui.showLoading(false);
            } catch (error) {
                console.error('Feil ved henting av brukerdata:', error);
                ui.showNotification('Kunne ikke hente brukerdata: ' + error.message, 'error');
                ui.showLoading(false);
                return;
            }
        } else {
            // Oppretting: Nullstill aktiv bruker
            this.activeUser = null;
            document.getElementById('user-id').value = '';
        }
        
        // Vis modal
        modal.style.display = 'block';
    },
    
    // Fyll inn tilgjengelige roller i brukermodal
    populateRoles: async function() {
        const rolesContainer = document.getElementById('roles-container');
        if (!rolesContainer) return;
        
        // Hvis vi ikke har roller ennå, last dem
        if (this.availableRoles.length === 0) {
            try {
                await this.loadRoles();
            } catch (error) {
                console.error('Feil ved lasting av roller:', error);
                rolesContainer.innerHTML = '<div class="error-message">Kunne ikke laste roller</div>';
                return;
            }
        }
        
        // Bygg HTML for rollecheckbokser
        let html = '';
        
        if (this.availableRoles.length > 0) {
            this.availableRoles.forEach(role => {
                html += `
                    <div class="role-checkbox">
                        <input type="checkbox" id="role-${role.id}" name="roles" value="${role.name}">
                        <label for="role-${role.id}">${role.display_name || role.name}</label>
                    </div>
                `;
            });
        } else {
            html = '<div class="error-message">Ingen roller tilgjengelig</div>';
        }
        
        rolesContainer.innerHTML = html;
    },
    
    // Lagre bruker (opprett eller oppdater)
    saveUser: async function() {
        const form = document.getElementById('user-form');
        if (!form) return;
        
        // Validering
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const userId = document.getElementById('user-id').value;
        
        if (!username || !email) {
            ui.showNotification('Brukernavn og e-post er påkrevd', 'error');
            return;
        }
        
        // Sjekk passordregler hvis passord er angitt eller ny bruker opprettes
        if ((password && password.length > 0) || !userId) {
            if (!password) {
                ui.showNotification('Passord er påkrevd for nye brukere', 'error');
                return;
            }
            
            if (password.length < 8) {
                ui.showNotification('Passord må være minst 8 tegn', 'error');
                return;
            }
            
            const hasNumber = /\d/.test(password);
            const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
            
            if (!hasNumber || !hasSpecial) {
                ui.showNotification('Passord må inneholde både tall og spesialtegn', 'error');
                return;
            }
        }
        
        // Samle brukerdata
        const userData = {
            username,
            email,
            full_name: document.getElementById('full-name').value,
            status: document.getElementById('status').value,
            roles: Array.from(document.querySelectorAll('input[name="roles"]:checked'))
                .map(cb => cb.value)
        };
        
        // Legg til passord hvis angitt
        if (password) {
            userData.password = password;
        }
        
        try {
            ui.showLoading(true);
            
            if (userId) {
                // Oppdater eksisterende bruker
                const endpoint = this.endpoints.user.replace(':id', userId);
                await api.put(endpoint, userData);
                ui.showNotification('Bruker oppdatert', 'success');
            } else {
                // Opprett ny bruker
                await api.post(this.endpoints.users, userData);
                ui.showNotification('Bruker opprettet', 'success');
            }
            
            // Last inn brukere på nytt og lukk modal
            await this.loadUsers();
            this.closeModals();
        } catch (error) {
            console.error('Feil ved lagring av bruker:', error);
            ui.showNotification('Kunne ikke lagre bruker: ' + error.message, 'error');
        } finally {
            ui.showLoading(false);
        }
    },
    
    // Vis bekreftelsesdialog for sletting
    showDeleteConfirmation: function(userId) {
        const modal = document.getElementById('confirm-modal');
        const message = document.getElementById('confirm-message');
        
        if (!modal || !message) return;
        
        // Lagre bruker-ID for sletting
        this.userToDelete = userId;
        
        // Sett bekreftelsesmelding
        message.textContent = 'Er du sikker på at du vil slette denne brukeren? Denne handlingen kan ikke angres.';
        
        // Vis modal
        modal.style.display = 'block';
    },
    
    // Slett bruker
    deleteUser: async function(userId) {
        if (!userId) return;
        
        try {
            ui.showLoading(true);
            
            const endpoint = this.endpoints.user.replace(':id', userId);
            await api.delete(endpoint);
            
            ui.showNotification('Bruker slettet', 'success');
            
            // Last inn brukere på nytt
            await this.loadUsers();
        } catch (error) {
            console.error('Feil ved sletting av bruker:', error);
            ui.showNotification('Kunne ikke slette bruker: ' + error.message, 'error');
        } finally {
            ui.showLoading(false);
        }
    },
    
    // Lukk alle modaler
    closeModals: function() {
        const userModal = document.getElementById('user-modal');
        const confirmModal = document.getElementById('confirm-modal');
        
        if (userModal) userModal.style.display = 'none';
        if (confirmModal) confirmModal.style.display = 'none';
        
        // Nullstill lagrede verdier
        this.userToDelete = null;
    }
};

// Export to global window object for UIManager
// UIManager looks for window.usersView when loading 'users' view
window.usersView = userManagementView;
