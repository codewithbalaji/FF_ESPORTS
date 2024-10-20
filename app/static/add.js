// Example 1: Handling Undefined Properties
const user = {
    name: "Alice",
    age: 25
};

// Accessing an existing property
console.log(user.name); // Output: Alice

// Accessing a non-existent property safely
if (user.email !== undefined) {
    console.log(user.email); // This won't execute
} else {
    console.log("Email property does not exist."); // Output: Email property does not exist.
}

// Example 2: TypeError Handling
let car = null;

// Checking if 'car' is not null before accessing properties
if (car !== null) {
    console.log(car.make);
} else {
    console.log("Car is not defined."); // Output: Car is not defined.
}

// Example 3: Read-Only Property
const readOnlyObject = {};
Object.defineProperty(readOnlyObject, 'immutable', {
    value: 42,
    writable: false // This property cannot be changed
});

// Trying to change a read-only property
try {
    readOnlyObject.immutable = 100; // This will throw an error
} catch (e) {
    console.error("Error: Cannot assign to read-only property 'immutable'"); // Output: Error: Cannot assign to read-only property 'immutable'
}

// Example 4: Accessing Non-Existent DOM Elements
const nonExistentElement = document.getElementById('someNonExistentId');

// Checking if the element exists before accessing its properties
if (nonExistentElement) {
    console.log(nonExistentElement.innerHTML);
} else {
    console.log("Element does not exist in the DOM."); // Output: Element does not exist in the DOM.
}

// Example 5: Incorrect Property Names
const carObject = {
    make: "Toyota",
    model: "Camry"
};

// Accessing property with incorrect name
console.log(carObject.make); // Output: Toyota
console.log(carObject.mak); // Output: undefined, should be carObject.make

// Example 6: Handling 'this' Context
const person = {
    name: "John",
    getName: function() {
        return this.name;
    }
};

// Works as expected
console.log(person.getName()); // Output: John

const getNameFunction = person.getName;

// Calling getNameFunction will not work as expected
console.log(getNameFunction()); // Output: undefined

// Fixing the context with bind
const boundGetName = getNameFunction.bind(person);
console.log(boundGetName()); // Output: John

// Example 7: Using Optional Chaining (ES2020)
const product = {
    id: 1,
    name: "Laptop",
    details: {
        brand: "BrandName"
    }
};

// Accessing properties safely with optional chaining
console.log(product.details?.brand); // Output: BrandName
console.log(product.details?.price); // Output: undefined (no error)

// Example 8: Default Values Using Nullish Coalescing
const userWithDefault = {
    name: "Alice"
};

// Using nullish coalescing to set a default value for missing properties
const age = userWithDefault.age ?? "Not specified";
console.log(age); // Output: Not specified
