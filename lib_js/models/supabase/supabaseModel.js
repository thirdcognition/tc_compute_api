// Import the validate function from the uuid package
import { validate as validateUUID } from "uuid";
import { v4 as uuidv4 } from "uuid";
import { throwApiError } from "../../helpers/errors.js";

function castToType(type, value) {
    if (typeof type === "string") {
        switch (type.toLowerCase()) {
            case "string":
                return String(value);
            case "number": {
                const num = Number(value);
                if (isNaN(num)) {
                    throw new Error(`Cannot cast value "${value}" to Number`);
                }
                return num;
            }
            case "boolean":
                return value === "true" || value === true;
            case "date": {
                const date = new Date(value);
                if (isNaN(date.getTime())) {
                    throw new Error(`Cannot cast value "${value}" to Date`);
                }
                return date;
            }
            default:
                return value;
        }
    } else if (typeof type === "function") {
        if (type.prototype.fromValue) {
            const enumInstance = new type();
            return enumInstance.fromValue(value);
        }
        // Assuming "type" is a class or constructor function
        try {
            return new type(value);
        } catch (e) {
            console.error(
                `Failed to cast value to ${typeof type}, error: ${e}`
            );
            return value;
        }
    } else if (
        typeof type === "object" &&
        Object.values(type).includes(value)
    ) {
        // Handle enums like ProcessStateEnum
        return value;
    } else {
        throw new Error(
            `Invalid type argument: "${typeof type}" with value("${value}")`
        );
    }
}

export class SupabaseModel {
    static TABLE_NAME = "";
    static TABLE_FIELDS = {};

    constructor(args) {
        this.attributes = {}; // Combined object for data, dataTypes, and dbColumn
        this.dirty = true;
        this.listeners = []; // Array to store listener callbacks
        this.boundNotifyListeners = (...args) => this.notifyListeners(...args);
        for (const [key, field] of Object.entries(
            this.constructor.TABLE_FIELDS
        )) {
            const val =
                key in args
                    ? args[key]
                    : this.constructor.mapKeyToDbColumn(key) in args
                      ? args[this.constructor.mapKeyToDbColumn(key)]
                      : undefined;
            this.attributes[key] =
                val !== undefined
                    ? castToType(field.type, val)
                    : field.type === "uuid" && field.required
                      ? uuidv4()
                      : null;
        }

        return new Proxy(this, {
            get(target, prop) {
                // console.log("get", prop);
                if (
                    prop === "constructor" ||
                    prop === "prototype" ||
                    typeof target[prop] === "function"
                ) {
                    return target[prop];
                }
                if (prop === "TABLE_NAME" || prop === "TABLE_FIELDS") {
                    return target.constructor[prop];
                }
                if (
                    prop === "dirty" ||
                    prop === "attributes" ||
                    prop === "listeners"
                ) {
                    return target[prop];
                }
                if (prop in target.attributes) {
                    return target.getAttribute(prop);
                }
                const asDbColumn = target.constructor.mapKeyToDbColumn(prop);
                if (asDbColumn in target.attributes) {
                    return target.getAttribute(asDbColumn);
                }
                // Allow access to function properties via the prototype if they exist
                if (prop in target.constructor.prototype) {
                    return target.constructor.prototype[prop];
                }
                // Allow access to static methods on the constructor
                if (prop in target.constructor) {
                    return target.constructor[prop];
                }
                // throw new Error(`${prop} is not a valid attribute`);
            },
            set(target, prop, value) {
                if (prop in target.attributes) {
                    target.setAttribute(prop, value);
                    return true;
                }
                const asDbColumn = target.constructor.mapKeyToDbColumn(prop);
                if (asDbColumn in target.attributes) {
                    target.setAttribute(asDbColumn, value);
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
                } else if (prop === "dirty" || prop === "listeners") {
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

    listen(callback) {
        if (
            typeof callback === "function" &&
            this.listeners.indexOf(callback) === -1
        ) {
            this.listeners.push(callback);
        }
        return this;
    }

    notifyListeners(...args) {
        this.listeners = this.listeners.filter(
            (listener) => listener(this, ...args) !== false
        );
    }

    getAttribute(name) {
        if (name in this.attributes) {
            return this.attributes[name];
        }
        return undefined;
    }

    setAttribute(name, value) {
        if (this.attributes[name] !== value) {
            if (this.constructor.validateAttribute(name, value)) {
                this.dirty = true;
                this.attributes[name] = value;
                this.notifyListeners(); // Notify listeners on attribute set
            } else {
                throw new Error(`Invalid value ${value} for attribute ${name}`);
            }
        }
    }

    static validateAttribute(name, value) {
        const config = this.TABLE_FIELDS[name];

        if (!config) {
            return true; // No type defined, assume valid
        }

        const { type, required } = config;
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
        // await supabase.getSession();
        return await this.saveToSupabase(supabase, this);
    }

    async read(supabase, idColumn = "id") {
        const value = this.attributes[idColumn];
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
        const value = this.attributes[idColumn];
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
        const value = this.attributes[idColumn];
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
                .select();
            const idToUpdatedData = {};
            if (response.error) {
                throwApiError(response);
            }
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
                        (field) => instance.attributes[field]
                    );
                } else {
                    instanceId = instance.attributes[idColumn];
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

            onConflict = this.replaceKeysWithDbColumns(onConflict);

            if (onConflict.length === 1) {
                response = await supabase
                    .from(this.TABLE_NAME)
                    .upsert(this.mapToDbColumns(data), { onConflict })
                    .select();
            } else {
                let query = supabase.from(this.TABLE_NAME).select("*");
                for (const key of onConflict) {
                    query = query.eq(key, data[key]);
                }
                response = await query; //await query.select();
                if (response.data && response.data.length > 0) {
                    query = supabase
                        .from(this.TABLE_NAME)
                        .update(this.mapToDbColumns(data));
                    for (const key of onConflict) {
                        query = query.eq(key, data[key]);
                    }
                    response = await query.select();
                } else {
                    response = await supabase
                        .from(this.TABLE_NAME)
                        .insert(this.mapToDbColumns(data))
                        .select();
                }
            }

            if (response.error) {
                console.error(response, data);
                throwApiError(response);
            }

            if (response.data && response.data.length > 0) {
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

        if (value === null || value === undefined) {
            throw new Error(`Value for '\${idColumn}' must be provided.`);
        }
        let query = supabase.from(this.TABLE_NAME).select("*");

        if (typeof value === "object") {
            for (const key in value) {
                const dbColumn = this.TABLE_FIELDS[key]?.dbColumn || key;
                query = query.eq(dbColumn, value[key]);
            }
        } else {
            const dbColumn = this.TABLE_FIELDS[idColumn]?.dbColumn || idColumn;
            query = query.eq(dbColumn, value);
        }

        const response = await query; //.select();

        if (response.error) {
            throwApiError(response);
        }
        const data =
            response.data && response.data.length > 0 ? response.data[0] : null;

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
                    const dbColumn = this.TABLE_FIELDS[key]?.dbColumn || key;
                    query = query.eq(dbColumn, filter[key]);
                }
            } else {
                const dbColumn =
                    this.TABLE_FIELDS[idColumn]?.dbColumn || idColumn;
                query = query.eq(dbColumn, filter);
            }
        }

        if (values !== null && values !== undefined) {
            if (typeof values === "string") {
                values = [values];
            }
            const strValues = [];
            for (const value of values) {
                if (typeof value === "object" && !Array.isArray(value)) {
                    for (const key in value) {
                        const dbColumn =
                            this.TABLE_FIELDS[key]?.dbColumn || key;
                        query = query.in(dbColumn, value[key]);
                    }
                } else if (Array.isArray(value)) {
                    const dbColumn =
                        this.TABLE_FIELDS[idColumn]?.dbColumn || idColumn;
                    query = query.in(dbColumn, value);
                } else {
                    strValues.push(value);
                }
            }
            if (strValues.length > 0) {
                const dbColumn =
                    this.TABLE_FIELDS[idColumn]?.dbColumn || idColumn;
                query = query.in(dbColumn, strValues);
            }
        }

        const response = await query; //.select();
        if (response.error) {
            throwApiError(response);
        }
        if (!response.data || response.data.length === 0) {
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

        const response = await query; //.select();
        if (response.error) {
            throwApiError(response);
        }
        return response.data && response.data.length > 0;
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

        const response = await query; //.select();
        if (response.error) {
            throwApiError(response);
        }
        return response.data && response.data.length > 0;
    }

    modelDump(options = {}) {
        const data = {};
        for (const key in this.attributes) {
            data[this.TABLE_FIELDS[key].dbColumn] = this.attributes[key];
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
            const attributeName = this.mapDbColumnToKey(dbColumn);
            if (attributeName in this.TABLE_FIELDS) {
                this.attributes[attributeName] = dbData[dbColumn];
            }
        }
        this.dirty = false;
        this.notifyListeners(); // Notify listeners on update from DB data
    }

    static fromDbData(dbData) {
        // Create an object to hold mapped attribute names and their values
        const attributes = {};
        for (const dbColumn in dbData) {
            const attributeName = this.mapDbColumnToKey(dbColumn);
            attributes[attributeName] = dbData[dbColumn];
        }

        // Pass the attributes object directly to the constructor
        const instance = new this(attributes);
        instance.dirty = false;
        return instance;
    }

    static replaceKeysWithDbColumns(keys) {
        return keys.map((key) => this.TABLE_FIELDS[key]?.dbColumn || key);
    }

    static mapToDbColumns(data) {
        const mappedData = {};
        for (const key in data) {
            const dbColumn = this.TABLE_FIELDS[key]?.dbColumn || key;
            mappedData[dbColumn] = data[key];
        }
        return mappedData;
    }

    static mapKeyToDbColumn(key) {
        if (key in this.TABLE_FIELDS) {
            return this.TABLE_FIELDS[key].dbColumn;
        }
        return key;
    }

    static mapDbColumnToKey(dbColumn) {
        for (const key in this.TABLE_FIELDS) {
            if (this.TABLE_FIELDS[key].dbColumn === dbColumn) {
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
