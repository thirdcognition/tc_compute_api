// lib_js/tests/journeyTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import { JourneyModel } from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;

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

    it("should create a new journey", async function () {
        newJourney = new JourneyModel({
            organizationId: newOrg.id,
            disabled: false
        });
        newJourney = await newJourney.create(supabase);
        assert(newJourney !== null, "Journey should be created");
        assert.strictEqual(
            newJourney.organizationId,
            newOrg.id,
            "Journey organizationId should match"
        );
    });

    it("should fetch the journey", async function () {
        const fetchedJourney = await JourneyModel.fetchFromSupabase(
            supabase,
            newJourney.id
        );
        assert(fetchedJourney !== null, "Fetched journey should not be null");
        assert.strictEqual(
            fetchedJourney.id,
            newJourney.id,
            "Fetched journey ID should match"
        );
    });

    it("should update the journey", async function () {
        newJourney.disabled = true;
        await newJourney.update(supabase);
        const updatedJourney = await JourneyModel.fetchFromSupabase(
            supabase,
            newJourney.id
        );
        assert.strictEqual(
            updatedJourney.disabled,
            true,
            "Journey should be disabled"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey and organization
        if (newJourney && newJourney.id) {
            await JourneyModel.deleteFromSupabase(supabase, newJourney.id);
        }
        if (newOrg && newOrg.id) {
            await OrganizationsModel.deleteFromSupabase(supabase, newOrg.id);
        }
    });
});
