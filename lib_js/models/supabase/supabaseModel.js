// Import the validate function from the uuid package
import { validate as validateUUID } from "uuid";

class SupabaseModel {
    static TABLE_NAME = "";

    constructor() {
        this.attributes = {}; // Combined object for data, dataTypes, and dbColumn
        this.dirty = true;

        return new Proxy(this, {
            get(target, prop) {
                if (
                    prop === "dirty" ||
                    prop === "attributes" ||
                    prop === "TABLE_NAME"
                ) {
                    return target[prop];
                }
                if (prop in target.attributes) {
                    return target.getAttribute(prop);
                }
                throw new Error(`${prop} is not a valid attribute`);
            },
            set(target, prop, value) {
                if (prop in target.attributes) {
                    target.setAttribute(prop, value);
                    return true;
                } else if (prop === "attributes") {
                    for (const key in value) {
                        const attribute = value[key];
                        if (
                            !("type" in attribute) ||
                            (attribute.required && !("value" in attribute)) ||
                            !("dbColumn" in attribute)
                        ) {
                            throw new Error(
                                `Attribute ${key} must have 'type', 'dbColumn', 'required' and if required a 'value'.`
                            );
                        }
                    }
                    target[prop] = value;
                } else if (prop === "dirty") {
                    target[prop] = value;
                } else {
                    throw new Error(`${prop} is not a valid attribute`);
                }
                return true;
            },
            has(target, prop) {
                return (
                    prop in target.attributes ||
                    prop === "dirty" ||
                    prop === "attributes" ||
                    prop === "TABLE_NAME"
                );
            }
        });
    }

    getAttribute(name) {
        if (name in this.attributes) {
            return this.attributes[name].value;
        }
        return undefined;
    }

    setAttribute(name, value) {
        if (this.validateAttribute(name, value)) {
            this.attributes[name].value = value;
        } else {
            throw new Error(`Invalid value ${value} for attribute ${name}`);
        }
    }

    validateAttribute(name, value) {
        const attribute = this.attributes[name];
        if (!attribute) {
            return true; // No type defined, assume valid
        }

        const { type, required } = attribute;
        // Explicitly allow null values unless required
        const isValueNull = value === null;
        if (isValueNull) {
            return !required;
        }

        if (typeof type === "object" && typeof type.validate === "function") {
            return type.validate(value);
        }

        switch (type) {
            case "string":
                return typeof value === "string";
            case "number":
                return typeof value === "number";
            case "integer":
                return Number.isInteger(value);
            case "float":
                return typeof value === "number";
            case "boolean":
                return typeof value === "boolean";
            case "json":
                try {
                    JSON.parse(JSON.stringify(value));
                    return true;
                } catch (e) {
                    console.error(e);
                    return false;
                }
            case "array":
                return Array.isArray(value);
            case "date": {
                const dateValue = new Date(value);
                return !isNaN(dateValue.getTime());
            }
            case "timestamp": {
                const timestampValue = new Date(value);
                return !isNaN(timestampValue.getTime());
            }
            case "uuid":
                return typeof value === "string" && validateUUID(value);
            default:
                return true;
        }
    }

    async create(supabase) {
        return await this.saveToSupabase(supabase, this);
    }

    async read(supabase, idColumn = "id") {
        const value = this.attributes[idColumn]?.value;
        if (value === undefined) {
            throw new Error(`'${idColumn}' is not set for this instance.`);
        }
        return await this.constructor.fetchFromSupabase(
            supabase,
            value,
            idColumn,
            this
        );
    }

    async update(supabase) {
        return await this.saveToSupabase(supabase, this);
    }

    async delete(supabase, idColumn = "id") {
        const value = this.attributes[idColumn]?.value;
        if (value === undefined) {
            throw new Error(`'${idColumn}' is not set for this instance.`);
        }
        return await this.constructor.deleteFromSupabase(
            supabase,
            value,
            idColumn
        );
    }

    async exists(supabase, idColumn = "id") {
        const value = this.attributes[idColumn]?.value;
        if (value === undefined) {
            throw new Error(`'${idColumn}' is not set for this instance.`);
        }
        return await this.constructor.existsInSupabase(
            supabase,
            value,
            idColumn
        );
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["id"],
        idColumn = "id"
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

                // Convert enum types to strings
                for (const key in data) {
                    const value = data[key];
                    if (value instanceof Enum) {
                        data[key] = value.name;
                    }
                }

                upsertData.push(data);
            }
        }

        if (upsertData.length > 0) {
            const response = await supabase
                .from(this.TABLE_NAME)
                .upsert(
                    upsertData.map((instance) => this.mapToDbColumns(instance)),
                    { onConflict }
                )
                .execute();
            const idToUpdatedData = {};

            if (Array.isArray(idColumn)) {
                for (const item of response.data) {
                    const idKeys = idColumn.map((field) => item[field]);
                    idToUpdatedData[idKeys] = item;
                }
            } else {
                for (const item of response.data) {
                    idToUpdatedData[item[idColumn]] = item;
                }
            }

            for (const instance of instances) {
                let instanceId;
                if (Array.isArray(idColumn)) {
                    instanceId = idColumn.map(
                        (field) => instance.attributes[field]?.value
                    );
                } else {
                    instanceId = instance.attributes[idColumn]?.value;
                }

                if (
                    instance.dirty &&
                    instanceId &&
                    idToUpdatedData[instanceId]
                ) {
                    instance.updateFromDbData(idToUpdatedData[instanceId]);
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

            // Convert enum types to strings
            for (const key in data) {
                const value = data[key];
                if (value instanceof Enum) {
                    data[key] = value.name;
                }
            }

            if (!this.TABLE_NAME)
                throw new Error("TABLE_NAME must be set for the model.");

            let response;
            if (onConflict.length === 1) {
                response = await supabase
                    .from(this.TABLE_NAME)
                    .upsert(this.mapToDbColumns(data), { onConflict })
                    .execute();
            } else {
                let query = supabase.from(this.TABLE_NAME).select("*");
                for (const key of onConflict) {
                    query = query.eq(key, data[key]);
                }
                response = await query.execute();
                if (response.data.length > 0) {
                    query = supabase
                        .from(this.TABLE_NAME)
                        .update(this.mapToDbColumns(data));
                    for (const key of onConflict) {
                        query = query.eq(key, data[key]);
                    }
                    response = await query.execute();
                } else {
                    response = await supabase
                        .from(this.TABLE_NAME)
                        .insert(this.mapToDbColumns(data))
                        .execute();
                }
            }

            if (response.data.length > 0) {
                instance.updateFromDbData(response.data[0]);
            }
        }

        return instance;
    }

    static async fetchFromSupabase(
        supabase,
        value,
        idColumn = "id",
        instance = null
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).select("*");
        if (value === null || value === undefined) {
            throw new Error(`Value for '\${idColumn}' must be provided.`);
        }

        if (typeof value === "object") {
            for (const key in value) {
                const dbColumn = this.attributes[key]?.dbColumn || key;
                query = query.eq(dbColumn, value[key]);
            }
        } else {
            const dbColumn = this.attributes[idColumn]?.dbColumn || idColumn;
            query = query.eq(dbColumn, value);
        }

        const response = await query.execute();
        const data = response.data.length > 0 ? response.data[0] : null;

        if (data !== null) {
            if (!instance) {
                instance = this.fromDbData(data);
            } else {
                instance.fromDbData(data);
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
        idColumn = "id"
    ) {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).select("*");

        if (filter !== null) {
            if (typeof filter === "object") {
                for (const key in filter) {
                    const dbColumn = this.attributes[key]?.dbColumn || key;
                    query = query.eq(dbColumn, filter[key]);
                }
            } else {
                const dbColumn =
                    this.attributes[idColumn]?.dbColumn || idColumn;
                query = query.eq(dbColumn, filter);
            }
        }

        if (values.length > 0) {
            for (const value of values) {
                if (typeof value === "object") {
                    for (const key in value) {
                        const dbColumn = this.attributes[key]?.dbColumn || key;
                        query = query.in(dbColumn, value[key]);
                    }
                } else {
                    const dbColumn =
                        this.attributes[idColumn]?.dbColumn || idColumn;
                    query = query.in(dbColumn, value);
                }
            }
        }

        const response = await query.execute();
        if (response.data.length === 0) {
            return [];
        }

        return response.data.map((data) => this.fromDbData(data));
    }

    static async existsInSupabase(supabase, value = null, idColumn = "id") {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        const selectedFields = [idColumn];
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
            query = query.eq(idColumn, value);
        }

        const response = await query.execute();
        return response.data.length > 0;
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = "id") {
        if (!this.TABLE_NAME)
            throw new Error("TABLE_NAME must be set for the model.");

        let query = supabase.from(this.TABLE_NAME).delete();

        if (value === null || value === undefined) {
            throw new Error(
                `Value must be provided to delete an item based on '${idColumn}'.`
            );
        } else if (typeof value === "object") {
            for (const key in value) {
                query = query.eq(key, value[key]);
            }
        } else {
            query = query.eq(idColumn, value);
        }

        const response = await query.execute();
        return response.data.length > 0;
    }

    modelDump(options = {}) {
        const data = {};
        for (const key in this.attributes) {
            data[this.attributes[key].dbColumn] = this.attributes[key].value;
        }
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

    updateFromDbData(dbData) {
        for (const dbColumn in dbData) {
            const attributeName = this.mapFromDbColumns(dbColumn);
            if (attributeName in this.attributes) {
                this.attributes[attributeName].value = dbData[dbColumn];
            }
        }
        this.dirty = false;
    }

    static fromDbData(dbData) {
        // Create an object to hold mapped attribute names and their values
        const attributes = {};
        for (const dbColumn in dbData) {
            const attributeName = this.prototype.mapFromDbColumns(dbColumn);
            attributes[attributeName] = dbData[dbColumn];
        }

        // Pass the attributes object directly to the constructor
        const instance = new this(attributes);
        instance.dirty = false;
        return instance;
    }

    mapToDbColumns(data) {
        const mappedData = {};
        for (const key in data) {
            const dbColumn = this.attributes[key]?.dbColumn || key;
            mappedData[dbColumn] = data[key];
        }
        return mappedData;
    }

    mapFromDbColumns(dbColumn) {
        for (const key in this.attributes) {
            if (this.attributes[key].dbColumn === dbColumn) {
                return key;
            }
        }
        return dbColumn; // Default to dbColumn if no mapping found
    }
}

// New Enum class with a validate method
export class Enum {
    static validate(value) {
        return Object.values(this).includes(value);
    }
}

export default SupabaseModel;
