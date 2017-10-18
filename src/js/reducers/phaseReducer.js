function phaseReducerHelper(action, obj) {
    let tokens = action.type.split('_');

    if (tokens.length == 2) {
        tokens.push('');
    }
    switch (tokens[2]) {
        case '': {
            obj.fetching = true;
            obj.fetched = false;
            break;
        }
        case 'REJECTED': {
            obj.fetching = false;
            obj.fetched = true;
            obj.error = action.payload;
            obj.data = null;
            break;
        }
        case 'FULFILLED': {
            obj.fetching = false;
            obj.fetched = true;
            obj.error = null;
            obj.data = action.payload;
            break;
        }
    }
    if (obj.phaseID !== undefined) obj.phaseID = action.phaseID;

    return obj;
}

export default function reducer(state={
    phase: {
        id: null,
    },
    timeline: {
        data: [],
        similarityThreshold: 0,
        fetching: false,
        fetched: false,
        error: null,
    },
    treemap: {
        data: [],
        phaseID: -1,
        fetching: false,
        fetched: false,
        error: null,
    },
    code: {
        data: [],
        phaseID: -1,
        fetching: false,
        fetched: false,
        error: null,
    },
    prof: {
        data: {},
        phaseID: -1,
        fetching: false,
        fetched: false,
        error: null,
    },
}, action) {
    let tokens = action.type.split('_');

    // Find phase related fetch requests first
    if (tokens.length >= 2 && tokens[0] === 'FETCH') {
        switch (tokens[1]) {
            case 'TIMELINE': {
                return {...state, timeline: phaseReducerHelper(action, {...state.timeline})};
            }
            case 'TREEMAP': {
                return {...state, treemap: phaseReducerHelper(action, {...state.treemap})};
            }
            case 'CODE': {
                return {...state, code: phaseReducerHelper(action, {...state.code})};
            }
            case 'PROF': {
                return {...state, prof: phaseReducerHelper(action, {...state.prof})};
            }
        }
    }

    // Do other requests
    switch (action.type) {
        case 'SET_SELECTED_PHASE_ID': {
            return {
                ...state,
                phase: {...state.phase, id: action.payload},
            };
        }
        case 'SET_SIMILARITY_THRESHOLD': {
            return {...state, timeline: {...state.timeline, similarityThreshold: parseInt(action.payload)}};
        }
    }

    return state;
}
