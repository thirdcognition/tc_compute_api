import { createSupabaseClient } from "../supabaseClient.js";
import {
    UserData,
    UserOrganizationRequestData
} from "../models/data/userData.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { User } from "../models/user.js";
import { authenticate } from "./authTest.js";
import { ApiConfig } from "../helpers/ApiHelper.js";
import assert from "assert";
import dotenv from "dotenv";

dotenv.config();

const SERVER_HOST = process.env.SERVER_HOST || "";
const SERVER_PORT = process.env.SERVER_PORT || "";

describe("User Model Tests", function () {
    let supabase;
    let session;
    let newUser;
    let newOrg;

    before(async function () {
        // Authenticate and get access token
        session = await authenticate();
        supabase = await createSupabaseClient(session); // Create a client with the access token
    });

    it("should create a new organization", async function () {
        newOrg = new OrganizationsModel({
            name: "Test Organization",
            website: "https://test.com"
        });
        newOrg = await newOrg.create(supabase);
        assert(newOrg !== null, "Organization should be created");
    });

    it("should create a new user and verify model details", async function () {
        // Create a new organization user using UserData
        const requestData = new UserOrganizationRequestData(
            "user2@example.com",
            null,
            null,
            false
        );
        const apiConfig = new ApiConfig(
            SERVER_HOST,
            SERVER_PORT,
            session.access_token,
            session.refresh_token
        );
        newUser = await UserData.createOrganizationUser(
            supabase,
            newOrg.id,
            requestData,
            apiConfig
        );

        // Initialize the user
        const user = new User(supabase, newUser.authId);
        await user.initialize();

        // Verify the user model has expected details
        assert(user.model !== null, "User model should not be null");
        assert(user.model.profile !== null, "User profile should not be null");
        assert(
            Array.isArray(user.model.organizations),
            "User organizations should be an array"
        );
    });

    after(async function () {
        // Clean up by deleting the test organization
        if (newOrg && newOrg.id) {
            await OrganizationsModel.deleteFromSupabase(supabase, newOrg.id);
        }
    });
});
