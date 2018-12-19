export {states, base_state, temp_file, loadState, saveState};

let base_state = {
    states: [],
    environments: [],
    moves: [],
    out: "",

    index: 0,
    expr_i: 0,

    start: 0,
    end: 0,
    roots: ["demo"],

    globalFrameID: -1,

    editor_open: false,
    sub_open: false,
    env_open: false,
    turtle_open: false,
    out_open: false,
    tests_open: false,

    test_results: undefined,

    file_name: "",
};

let states = [jQuery.extend({}, base_state)];

let temp_file = "<temporary>";

function db(callback) {
    let request = indexedDB.open("state");

    let db;

    request.onupgradeneeded = function () {
        // The database did not previously exist, so create object stores and indexes.
        let db = request.result;
        let store = db.createObjectStore("state", {keyPath: "id"});
        let idIndex = store.createIndex("by_id", "id", {unique: true});
    };

    request.onsuccess = function () {
        db = request.result;
        callback(db);
        db.close();
    };
}

function store(db, callback) {
    let tx = db.transaction("state", "readwrite");
    let store = tx.objectStore("state");

    store.put({id: 1, state: states});

    tx.oncomplete = function() {
        console.log("Save complete!");
        if (callback !== undefined) {
            console.log(callback);
            callback();
        }
    };
}

function load(db, callback) {
    let tx = db.transaction("state", "readonly");
    let store = tx.objectStore("state");
    let index = store.index("by_id");

    let request = index.get(1);
    request.onsuccess = function() {
      let matching = request.result;
      if (matching !== undefined) {
          states = matching.state;
          console.log(states);
      } else {
        // No match was found.
      }
      callback();
    };
}

function loadState(callback) {
    db(function (db) {
        load(db, callback);
    });
}

function saveState(callback) {
    console.log("Starting save!");
    db(function (db) {
        store(db, callback);
    });}