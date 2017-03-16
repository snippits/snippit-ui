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
        data: [],
        fetching: false,
        fetched: false,
        error: null,
    },
}, action) {

    switch (action.type) {
        case "FETCH_TIMELINE": {
            return {...state,
                timeline: {...state.timeline, fetching: true, fetched:false, similarity_threshold: parseInt(action.payload)}}
        }
        case "FETCH_TIMELINE_REJECTED": {
            return {...state,
                timeline: {...state.timeline, fetching: false, fetched:true, error: action.payload}}
        }
        case "FETCH_TIMELINE_FULFILLED": {
            return {
                ...state,
                timeline: {...state.timeline,
                    fetching: false,
                    fetched: true,
                    data: action.payload,
                    error: null,
                },
            }
        }
        case "FETCH_TREEMAP": {
            return {...state,
                treemap: {...state.treemap, fetching: true, fetched:false}}
        }
        case "FETCH_TREEMAP_REJECTED": {
            return {...state,
                treemap: {...state.treemap, fetching: false, error: action.payload}}
        }
        case "FETCH_TREEMAP_FULFILLED": {
            return {
                ...state,
                treemap: {...state.treemap,
                    fetching: false,
                    fetched: true,
                    data: action.payload,
                    error: null,
                },
            }
        }
        case "FETCH_CODE": {
            return {...state,
                code: {...state.code, fetching: true, fetched:false}}
        }
        case "FETCH_CODE_REJECTED": {
            return {...state,
                code: {...state.code, fetching: false, error: action.payload}}
        }
        case "FETCH_CODE_FULFILLED": {
            return {
                ...state,
                code: {...state.code,
                    fetching: false,
                    fetched: true,
                    data: action.payload,
                    error: null,
                },
            }
        }
        case "FETCH_PROF": {
            return {...state,
                prof: {...state.prof, fetching: true, fetched:false}}
        }
        case "FETCH_PROF_REJECTED": {
            return {...state,
                prof: {...state.prof, fetching: false, error: action.payload}}
        }
        case "FETCH_PROF_FULFILLED": {
            return {
                ...state,
                prof: {...state.prof,
                    fetching: false,
                    fetched: true,
                    data: action.payload,
                    error: null,
                },
            }
        }
        case "SET_SELECTED_PHASE_ID": {
            return {
                ...state,
                phase: {...state.phase, id: action.payload},
            }
        }
    }

    return state
}
