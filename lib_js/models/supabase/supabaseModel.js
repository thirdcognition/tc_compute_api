class SupabaseModel {
    static TABLE_NAME = "";

    constructor() {
        this.dirty = true;
    }

    setAttribute(name, value) {
        if (name !== "dirty") {
            const currentValue = this[name];
            if (currentValue !== value) {
                this.dirty = true;
            }
        }
        this[name] = value;
    }

    async create(supabase) {
        return await this.saveToSupabase(supabase, this);
    }

    async read(supabase, value, idFieldName = "id") {
        return await this.fetchFromSupabase(supabase, value, idFieldName, this);
    }

    async update(supabase) {
        return await this.saveToSupabase(supabase, this);
    }

    async delete(supabase, value, idFieldName = "id") {
        return await this.deleteFromSupabase(supabase, value, idFieldName);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["id"],
        idFieldName = "id"
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        const upsertData = [];
        for (const instance of instances) {
            if (instance.dirty) {
                const data = instance.modelDump({
                    excludeNone: true,
                    excludeUnset: true
                });

                upsertData.push(data);
            }
        }

        if (upsertData.length > 0) {
            const response = await supabase
                .from(this.TABLE_NAME)
                .upsert(upsertData, { onConflict })
                .execute();
            const idToUpdatedData = {};

            if (Array.isArray(idFieldName)) {
                for (const item of response.data) {
                    const idKeys = idFieldName.map((field) => item[field]);
                    idToUpdatedData[idKeys] = item;
                }
            } else {
                for (const item of response.data) {
                    idToUpdatedData[item[idFieldName]] = item;
                }
            }

            for (const instance of instances) {
                let instanceId;
                if (Array.isArray(idFieldName)) {
                    instanceId = idFieldName.map((field) => instance[field]);
                } else {
                    instanceId = instance[idFieldName];
                }

                if (
                    instance.dirty &&
                    instanceId &&
                    idToUpdatedData[instanceId]
                ) {
                    const updatedData = idToUpdatedData[instanceId];
                    for (const key in updatedData) {
                        instance.setAttribute(key, updatedData[key]);
                    }
                }
                instance.dirty = false;
            }
        }

        return instances;
    }

    static async saveToSupabase(supabase, instance, onConflict = ["id"]) {
        if (instance.dirty) {
            const data = instance.modelDump({
                excludeNone: true,
                excludeUnset: true
            });

            if (!this.TABLE_NAME)
                throw new Error("TABLE_NAME must be set for the model.");

            let response;
            if (onConflict.length === 1) {
                response = await supabase
                    .from(this.TABLE_NAME)
                    .upsert(data, { onConflict })
                    .execute();
            } else {
                let query = supabase.from(this.TABLE_NAME).select("*");
                for (const key of onConflict) {
                    query = query.eq(key, data[key]);
                }
                response = await query.execute();
                if (response.data.length > 0) {
                    query = supabase.from(this.TABLE_NAME).update(data);
                    for (const key of onConflict) {
                        query = query.eq(key, data[key]);
                    }
                    response = await query.execute();
                } else {
                    response = await supabase
                        .from(this.TABLE_NAME)
                        .insert(data)
                        .execute();
                }
            }

            if (response.data.length > 0) {
                for (const key in response.data[0]) {
                    instance.setAttribute(key, response.data[0][key]);
                }
                instance.dirty = false;
            }
        }

        return instance;
    }

    static async fetchFromSupabase(
        supabase,
        value,
        idFieldName = "id",
        instance = null
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).select("*");
        if (value === null || value === undefined) {
            throw new Error(`Value for '${idFieldName}' must be provided.`);
        }

        if (typeof value === "object") {
            for (const key in value) {
                query = query.eq(key, value[key]);
            }
        } else {
            query = query.eq(idFieldName, value);
        }

        const response = await query.execute();
        const data = response.data.length > 0 ? response.data[0] : null;

        if (data !== null) {
            if (!instance) {
                instance = new this(data);
            } else {
                for (const key in data) {
                    instance.setAttribute(key, data[key]);
                }
            }
            instance.dirty = false;
            return instance;
        }

        return null;
    }

    static async fetchExistingFromSupabase(
        supabase,
        filter = null,
        values = [],
        idFieldName = "id"
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).select("*");

        if (filter !== null) {
            if (typeof filter === "object") {
                for (const key in filter) {
                    query = query.eq(key, filter[key]);
                }
            } else {
                query = query.eq(idFieldName, filter);
            }
        }

        if (values.length > 0) {
            for (const value of values) {
                if (typeof value === "object") {
                    for (const key in value) {
                        query = query.in(key, value[key]);
                    }
                } else {
                    query = query.in(idFieldName, value);
                }
            }
        }

        const response = await query.execute();
        if (response.data.length === 0) {
            return [];
        }

        return response.data.map((data) => new this(data));
    }

    static async existsInSupabase(supabase, value = null, idFieldName = "id") {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        const selectedFields = [idFieldName];
        if (typeof value === "object") {
            selectedFields.push(...Object.keys(value));
        }
        let query = supabase.from(this.TABLE_NAME).select(...selectedFields);

        if (value === null || value === undefined) {
            throw new Error("Value must be provided when using class method.");
        } else if (typeof value === "object") {
            for (const key in value) {
                query = query.eq(key, value[key]);
            }
        } else {
            query = query.eq(idFieldName, value);
        }

        const response = await query.execute();
        return response.data.length > 0;
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = "id"
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).delete();

        if (value === null || value === undefined) {
            throw new Error(
                `Value must be provided to delete an item based on '${idFieldName}'.`
            );
        } else if (typeof value === "object") {
            for (const key in value) {
                query = query.eq(key, value[key]);
            }
        } else {
            query = query.eq(idFieldName, value);
        }

        await query.execute();
        return true;
    }

    modelDump(options = {}) {
        const data = { ...this };
        delete data.TABLE_NAME;
        delete data.created_at;
        delete data.disabled_at;
        delete data.dirty;
        delete data.updated_by;
        delete data.updated_at;
        if (options.excludeNone) {
            for (const key in data) {
                if (data[key] === null || data[key] === undefined) {
                    delete data[key];
                }
            }
        }
        if (options.excludeUnset) {
            for (const key in data) {
                if (data[key] === undefined) {
                    delete data[key];
                }
            }
        }
        return data;
    }
}

export default SupabaseModel;
