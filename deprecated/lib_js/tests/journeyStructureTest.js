// lib_js/tests/journeyStructureTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import {
    JourneyStructureModel,
    JourneyModel
} from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Structure Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;
    let newJourneyStructure;

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

    it("should create a new journey structure", async function () {
        newJourneyStructure = new JourneyStructureModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id, // Use the created journey's ID
            disabled: false
        });
        newJourneyStructure = await newJourneyStructure.create(supabase);
        assert(
            newJourneyStructure !== null,
            "Journey structure should be created"
        );
        assert.strictEqual(
            newJourneyStructure.journeyId,
            newJourney.id,
            "Journey structure journeyId should match"
        );
    });

    it("should fetch the journey structure", async function () {
        const fetchedJourneyStructure =
            await JourneyStructureModel.fetchFromSupabase(
                supabase,
                newJourneyStructure.id
            );
        assert(
            fetchedJourneyStructure !== null,
            "Fetched journey structure should not be null"
        );
        assert.strictEqual(
            fetchedJourneyStructure.id,
            newJourneyStructure.id,
            "Fetched journey structure ID should match"
        );
    });

    it("should update the journey structure", async function () {
        newJourneyStructure.disabled = true;
        await newJourneyStructure.update(supabase);
        const updatedJourneyStructure =
            await JourneyStructureModel.fetchFromSupabase(
                supabase,
                newJourneyStructure.id
            );
        assert.strictEqual(
            updatedJourneyStructure.disabled,
            true,
            "Journey structure should be disabled"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey structure, journey, and organization
        if (newJourneyStructure && newJourneyStructure.id) {
            await JourneyStructureModel.deleteFromSupabase(
                supabase,
                newJourneyStructure.id
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
