// lib_js/tests/journeyVersionTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import {
    JourneyVersionModel,
    JourneyModel
} from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Version Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;
    let newJourneyVersion;

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

        // Create a new journey
        newJourney = new JourneyModel({
            organizationId: newOrg.id,
            disabled: false
        });
        newJourney = await newJourney.create(supabase);
    });

    it("should create a new journey version", async function () {
        newJourneyVersion = new JourneyVersionModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id, // Use the created journey's ID
            name: "Version 1",
            description: "Initial version"
        });
        newJourneyVersion = await newJourneyVersion.create(supabase);
        assert(newJourneyVersion !== null, "Journey version should be created");
        assert.strictEqual(
            newJourneyVersion.journeyId,
            newJourney.id,
            "Journey version journeyId should match"
        );
    });

    it("should fetch the journey version", async function () {
        const fetchedJourneyVersion =
            await JourneyVersionModel.fetchFromSupabase(
                supabase,
                newJourneyVersion.id
            );
        assert(
            fetchedJourneyVersion !== null,
            "Fetched journey version should not be null"
        );
        assert.strictEqual(
            fetchedJourneyVersion.id,
            newJourneyVersion.id,
            "Fetched journey version ID should match"
        );
    });

    it("should update the journey version", async function () {
        newJourneyVersion.description = "Updated version description";
        await newJourneyVersion.update(supabase);
        const updatedJourneyVersion =
            await JourneyVersionModel.fetchFromSupabase(
                supabase,
                newJourneyVersion.id
            );
        assert.strictEqual(
            updatedJourneyVersion.description,
            "Updated version description",
            "Journey version description should be updated"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey version, journey, and organization
        if (newJourneyVersion && newJourneyVersion.id) {
            await JourneyVersionModel.deleteFromSupabase(
                supabase,
                newJourneyVersion.id
            );
        }
        if (newJourney && newJourney.id) {
            await JourneyModel.deleteFromSupabase(supabase, newJourney.id);
        }
        if (newOrg && newOrg.id) {
            await OrganizationsModel.deleteFromSupabase(supabase, newOrg.id);
        }
    });
});
