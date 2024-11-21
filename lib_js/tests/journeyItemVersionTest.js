// lib_js/tests/journeyItemVersionTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import {
    JourneyItemVersionModel,
    JourneyItemModel,
    JourneyModel
} from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Item Version Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;
    let newJourneyItem;
    let newJourneyItemVersion;

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

        // Create a new journey item
        newJourneyItem = new JourneyItemModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id,
            disabled: false
        });
        newJourneyItem = await newJourneyItem.create(supabase);
    });

    it("should create a new journey item version", async function () {
        newJourneyItemVersion = new JourneyItemVersionModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id,
            journeyItemId: newJourneyItem.id,
            name: "Version 1",
            disabled: false
        });
        newJourneyItemVersion = await newJourneyItemVersion.create(supabase);
        assert(
            newJourneyItemVersion !== null,
            "Journey item version should be created"
        );
        assert.strictEqual(
            newJourneyItemVersion.journeyItemId,
            newJourneyItem.id,
            "Journey item version journeyItemId should match"
        );
    });

    it("should fetch the journey item version", async function () {
        const fetchedJourneyItemVersion =
            await JourneyItemVersionModel.fetchFromSupabase(
                supabase,
                newJourneyItemVersion.id
            );
        assert(
            fetchedJourneyItemVersion !== null,
            "Fetched journey item version should not be null"
        );
        assert.strictEqual(
            fetchedJourneyItemVersion.id,
            newJourneyItemVersion.id,
            "Fetched journey item version ID should match"
        );
    });

    it("should update the journey item version", async function () {
        newJourneyItemVersion.disabled = true;
        await newJourneyItemVersion.update(supabase);
        const updatedJourneyItemVersion =
            await JourneyItemVersionModel.fetchFromSupabase(
                supabase,
                newJourneyItemVersion.id
            );
        assert.strictEqual(
            updatedJourneyItemVersion.disabled,
            true,
            "Journey item version should be disabled"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey item version, journey item, journey, and organization
        if (newJourneyItemVersion && newJourneyItemVersion.id) {
            await JourneyItemVersionModel.deleteFromSupabase(
                supabase,
                newJourneyItemVersion.id
            );
        }
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
