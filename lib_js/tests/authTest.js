// lib_js/tests/authTest.js

import { supabase } from "../supabaseClient.js";

// Function to authenticate and get access token
async function authenticate() {
    const { data, error } = await supabase.auth.signInWithPassword({
        email: "user1@example.com",
        password: "password123"
    });

    if (error) {
        throw new Error(`Failed to authenticate: ${error.message}`);
    }

    return data.session;
}

export { authenticate };
