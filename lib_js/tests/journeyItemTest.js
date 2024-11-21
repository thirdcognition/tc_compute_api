// lib_js/tests/journeyItemTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import { JourneyItemModel, JourneyModel } from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Item Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;
    let newJourneyItem;

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

    it("should create a new journey item", async function () {
        newJourneyItem = new JourneyItemModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id, // Use the created journey's ID
            disabled: false
        });
        newJourneyItem = await newJourneyItem.create(supabase);
        assert(newJourneyItem !== null, "Journey item should be created");
        assert.strictEqual(
            newJourneyItem.journeyId,
            newJourney.id,
            "Journey item journeyId should match"
        );
    });

    it("should fetch the journey item", async function () {
        const fetchedJourneyItem = await JourneyItemModel.fetchFromSupabase(
            supabase,
            newJourneyItem.id
        );
        assert(
            fetchedJourneyItem !== null,
            "Fetched journey item should not be null"
        );
        assert.strictEqual(
            fetchedJourneyItem.id,
            newJourneyItem.id,
            "Fetched journey item ID should match"
        );
    });

    it("should update the journey item", async function () {
        newJourneyItem.disabled = true;
        await newJourneyItem.update(supabase);
        const updatedJourneyItem = await JourneyItemModel.fetchFromSupabase(
            supabase,
            newJourneyItem.id
        );
        assert.strictEqual(
            updatedJourneyItem.disabled,
            true,
            "Journey item should be disabled"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey item, journey, and organization
        if (newJourneyItem && newJourneyItem.id) {
            await JourneyItemModel.deleteFromSupabase(
                supabase,
                newJourneyItem.id
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
