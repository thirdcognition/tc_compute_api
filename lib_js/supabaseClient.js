// lib_js/supabaseClient.js

import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

// Load environment variables from .env file
dotenv.config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

function inMemoryStorageProvider() {
    const items = new Map();
    return {
        getItem: (key) => {
            // console.info("get item", key, items.get(key));
            return items.get(key);
        },
        setItem: (key, value) => {
            // console.info("set store item", key, value);
            items.set(key, value);
        },
        removeItem: (key) => {
            items.delete(key);
        }
    };
}

const store = inMemoryStorageProvider();

export const createSupabaseClient = async (session = null) => {
    const options = session
        ? {
              auth: {
                  storage: store,
                  autoRefreshToken: false
              },
              global: {
                  headers: {
                      Authorization: `Bearer ${session.access_token}`
                  }
              }
          }
        : {
              auth: {
                  storage: store,
                  autoRefreshToken: false
              }
          };
    const sbClient = createClient(SUPABASE_URL, SUPABASE_KEY, options);
    if (session) {
        // console.log("refresh", await sbClient.auth.refreshSession());
        await sbClient.auth.setSession(session);
    }

    return sbClient;
};

export const supabase = await createSupabaseClient();
