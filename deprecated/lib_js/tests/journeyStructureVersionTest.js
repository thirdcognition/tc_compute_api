// lib_js/tests/journeyStructureVersionTest.js

import { createSupabaseClient } from "../supabaseClient.js";
import {
    JourneyStructureVersionModel,
    JourneyStructureModel,
    JourneyModel,
    JourneyItemVersionModel,
    JourneyItemModel
} from "../models/supabase/journey.js";
import { OrganizationsModel } from "../models/supabase/organization.js";
import { authenticate } from "./authTest.js";
import assert from "assert";

describe("Journey Structure Version Model Tests", function () {
    let supabase;
    let session;
    let newOrg;
    let newJourney;
    let newJourneyStructure;
    let newJourneyItem;
    let newJourneyItemVersion;
    let newJourneyStructureVersion;

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

        // Create a new journey item version
        newJourneyItemVersion = new JourneyItemVersionModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id,
            journeyItemId: newJourneyItem.id,
            name: "Version 1",
            disabled: false
        });
        newJourneyItemVersion = await newJourneyItemVersion.create(supabase);

        // Create a new journey structure
        newJourneyStructure = new JourneyStructureModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id,
            disabled: false
        });
        newJourneyStructure = await newJourneyStructure.create(supabase);
    });

    it("should create a new journey structure version", async function () {
        newJourneyStructureVersion = new JourneyStructureVersionModel({
            organizationId: newOrg.id,
            journeyId: newJourney.id,
            journeyItemId: newJourneyItem.id, // Correctly use the journey item's ID
            journeyItemVersionId: newJourneyItemVersion.id, // Correctly use journeyItemVersionId
            versionOfId: newJourneyStructure.id,
            disabled: false
        });
        newJourneyStructureVersion =
            await newJourneyStructureVersion.create(supabase);
        assert(
            newJourneyStructureVersion !== null,
            "Journey structure version should be created"
        );
        assert.strictEqual(
            newJourneyStructureVersion.versionOfId,
            newJourneyStructure.id,
            "Journey structure version journeyItemId should match"
        );
    });

    it("should fetch the journey structure version", async function () {
        const fetchedJourneyStructureVersion =
            await JourneyStructureVersionModel.fetchFromSupabase(
                supabase,
                newJourneyStructureVersion.id
            );
        assert(
            fetchedJourneyStructureVersion !== null,
            "Fetched journey structure version should not be null"
        );
        assert.strictEqual(
            fetchedJourneyStructureVersion.id,
            newJourneyStructureVersion.id,
            "Fetched journey structure version ID should match"
        );
    });

    it("should update the journey structure version", async function () {
        newJourneyStructureVersion.disabled = true;
        await newJourneyStructureVersion.update(supabase);
        const updatedJourneyStructureVersion =
            await JourneyStructureVersionModel.fetchFromSupabase(
                supabase,
                newJourneyStructureVersion.id
            );
        assert.strictEqual(
            updatedJourneyStructureVersion.disabled,
            true,
            "Journey structure version should be disabled"
        );
    });

    after(async function () {
        // Clean up by deleting the test journey structure version, journey structure, journey item version, journey item, journey, and organization
        if (newJourneyStructureVersion && newJourneyStructureVersion.id) {
            await JourneyStructureVersionModel.deleteFromSupabase(
                supabase,
                newJourneyStructureVersion.id
            );
        }
        if (newJourneyStructure && newJourneyStructure.id) {
            await JourneyStructureModel.deleteFromSupabase(
                supabase,
                newJourneyStructure.id
            );
        }
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
