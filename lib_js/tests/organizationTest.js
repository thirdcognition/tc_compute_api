// lib_js/tests/organizationTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import {
    OrganizationsModel,
    OrganizationUsersModel
} from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Organizations Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let fetchedUser;

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
        assert.strictEqual(
            newOrg.name,
            "Test Organization",
            "Organization name should match"
        );
    });

    it("should fetch the organization", async function () {
        const fetchedOrg = await OrganizationsModel.fetchFromSupabase(
            supabase,
            newOrg.id
        );
        assert(fetchedOrg !== null, "Fetched organization should not be null");
        assert.strictEqual(
            fetchedOrg.id,
            newOrg.id,
            "Fetched organization ID should match"
        );
    });

    it("should update the organization", async function () {
        newOrg.website = "https://updated-test.com";
        await newOrg.update(supabase);
        const updatedOrg = await OrganizationsModel.fetchFromSupabase(
            supabase,
            newOrg.id
        );
        assert.strictEqual(
            updatedOrg.website,
            "https://updated-test.com",
            "Organization website should be updated"
        );
    });

    it("should fetch the user", async function () {
        fetchedUser = await OrganizationUsersModel.fetchFromSupabase(
            supabase,
            session.user.id,
            "auth_id"
        );
        assert(fetchedUser !== null, "Fetched user should not be null");
        assert.strictEqual(
            fetchedUser.authId,
            session.user.id,
            "Fetched user auth_id should match"
        );
    });

    it("should update the user", async function () {
        fetchedUser.metadata = { metadata: "test" };
        await fetchedUser.update(supabase);
        const updatedUser = await OrganizationUsersModel.fetchFromSupabase(
            supabase,
            fetchedUser
        );
        assert.deepStrictEqual(
            updatedUser.metadata,
            { metadata: "test" },
            "User metadata should be updated"
        );
    });

    after(async function () {
        // Clean up by deleting the test user and organization
        if (newOrg && newOrg.id) {
            await OrganizationsModel.deleteFromSupabase(supabase, newOrg.id);
        }
    });
});
