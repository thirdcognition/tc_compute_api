// lib_js/tests/aclTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import { ACLGroupModel } from "../models/supabase/acl.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("ACL Group Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newGroup;

    before(async function () {
        // Authenticate and get access token
        session = await authenticate();
        supabase = await createSupabaseClient(session); // Create a client with the access token

        // Create a new organization
        newOrg = new OrganizationsModel({
            name: "Test Organization",
            website: "https://test.com"
        });
        newOrg = await newOrg.create(supabase);
    });

    it("should create a new ACL group", async function () {
        newGroup = new ACLGroupModel({
            name: "Test Group",
            description: "A test group for ACL",
            organizationId: newOrg.id // Use the created organization's ID
        });
        newGroup = await newGroup.create(supabase);
        assert(newGroup !== null, "ACL group should be created");
        assert.strictEqual(
            newGroup.name,
            "Test Group",
            "ACL group name should match"
        );
    });

    it("should fetch the ACL group", async function () {
        const fetchedGroup = await ACLGroupModel.fetchFromSupabase(
            supabase,
            newGroup.id
        );
        assert(fetchedGroup !== null, "Fetched ACL group should not be null");
        assert.strictEqual(
            fetchedGroup.id,
            newGroup.id,
            "Fetched ACL group ID should match"
        );
    });

    after(async function () {
        // Clean up by deleting the test ACL group and organization
        if (newGroup && newGroup.id) {
            await ACLGroupModel.deleteFromSupabase(supabase, newGroup.id);
        }
        if (newOrg && newOrg.id) {
            await OrganizationsModel.deleteFromSupabase(supabase, newOrg.id);
        }
    });
});
