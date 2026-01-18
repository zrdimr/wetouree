// Firebase Configuration
// Replace these values with your Firebase project credentials
// Get them from: Firebase Console > Project Settings > Web App

const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const provider = new firebase.auth.GoogleAuthProvider();

// Auth State Observer
let currentUser = null;

auth.onAuthStateChanged((user) => {
    currentUser = user;
    updateAuthUI(user);

    if (user) {
        // Send user info to backend session
        fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uid: user.uid,
                email: user.email,
                displayName: user.displayName,
                photoURL: user.photoURL
            })
        });
    }
});

// Google Sign In
async function signInWithGoogle() {
    try {
        const result = await auth.signInWithPopup(provider);
        console.log('Signed in:', result.user.email);
        return result.user;
    } catch (error) {
        console.error('Sign in error:', error);
        alert('Login gagal: ' + error.message);
    }
}

// Sign Out
async function signOut() {
    try {
        await auth.signOut();
        await fetch('/api/auth/logout', { method: 'POST' });
        console.log('Signed out');
        window.location.reload();
    } catch (error) {
        console.error('Sign out error:', error);
    }
}

// Update UI based on auth state
function updateAuthUI(user) {
    const authBtn = document.getElementById('authButton');
    const userInfo = document.getElementById('userInfo');

    if (authBtn && userInfo) {
        if (user) {
            authBtn.style.display = 'none';
            userInfo.style.display = 'flex';
            userInfo.innerHTML = `
                <img src="${user.photoURL || 'https://via.placeholder.com/32'}" 
                     alt="Profile" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 8px;">
                <span style="margin-right: 10px;">${user.displayName || user.email}</span>
                <button onclick="signOut()" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer;">Logout</button>
            `;
        } else {
            authBtn.style.display = 'block';
            userInfo.style.display = 'none';
        }
    }
}

// Check if user is logged in before booking
function requireAuth(callback) {
    if (currentUser) {
        callback();
    } else {
        alert('Silakan login terlebih dahulu untuk melakukan booking');
        signInWithGoogle().then(() => {
            if (currentUser) callback();
        });
    }
}
