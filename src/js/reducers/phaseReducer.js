function phaseReducerHelper(action, obj) {
    var type_array = action.type.split("_");

    if (type_array.length == 2) {
        type_array.push("");
    }
    switch (type_array[2]) {
        case "": {
            obj.fetching = true;
            obj.fetched = false;
            break;
        }
        case "REJECTED": {
            obj.fetching = false;
            obj.fetched = true;
            obj.error = action.payload;
            obj.data = null;
            break;
        }
        case "FULFILLED": {
            obj.fetching = false;
            obj.fetched = true;
            obj.error = null;
            obj.data = action.payload;
            break;
        }
    }

    return obj;
}

export default function reducer(state={
    phase: {
        id: null,
    },
    timeline: {
        data: [],
        similarity_threshold: null,
        fetching: false,
        fetched: false,
        error: null,
    },
    treemap: {
        data: [],
        fetching: false,
        fetched: false,
        error: null,
    },
    code: {
        data: [],
        fetching: false,
        fetched: false,
        error: null,
    },
    prof: {
        data: {},
        fetching: false,
        fetched: false,
        error: null,
    },
}, action) {
    var type_array = action.type.split("_");

    // Find phase related fetch requests first
    if (type_array.length >= 2 && type_array[0] === "FETCH") {
        switch (type_array[1]) {
            case "TIMELINE": {
                return {...state, timeline: phaseReducerHelper(action, {...state.timeline})};
            }
            case "TREEMAP": {
                return {...state, treemap: phaseReducerHelper(action, {...state.treemap})};
            }
            case "CODE": {
                return {...state, code: phaseReducerHelper(action, {...state.code})};
            }
            case "PROF": {
                return {...state, prof: phaseReducerHelper(action, {...state.prof})};
            }
        }
    }

    // Do other requests
    switch (action.type) {
        case "SET_SELECTED_PHASE_ID": {
            return {
                ...state,
                phase: {...state.phase, id: action.payload},
            }
        }
        case "SET_SIMILARITY_THRESHOLD": {
            return {...state, timeline: {...state.timeline, similarity_threshold: parseInt(action.payload)}}
        }
    }

    return state
}
