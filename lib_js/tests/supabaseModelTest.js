import { SupabaseModel } from "../models/supabase/supabaseModel.js";
import assert from "assert";

describe("SupabaseModel Listener Tests", function () {
    it("should call listener when attribute is set", function () {
        const model = new SupabaseModel({});
        let listenerCalled = false;

        model.listen((instance) => {
            listenerCalled = true;
            assert.strictEqual(
                instance,
                model,
                "Listener should receive the model instance"
            );
        });

        model.setAttribute("testAttribute", "newValue");
        assert.strictEqual(
            listenerCalled,
            true,
            "Listener should be called when attribute is set"
        );
    });

    it("should remove listener if it returns false", function () {
        const model = new SupabaseModel({});
        let callCount = 0;

        model.listen(() => {
            callCount++;
            return false; // Returning false should remove the listener
        });

        model.setAttribute("testAttribute", "newValue");
        model.setAttribute("testAttribute", "anotherValue");

        assert.strictEqual(callCount, 1, "Listener should be called only once");
    });
});
