import axios from 'axios';

export function fetchInfo(query, id = null) {
    let link = 'query';

    return function(dispatch) {
        dispatch({id: id, type: 'FETCH_INFO'});
        axios.get(link, {
            params: {
                query: query,
            },
        }).then((response) => {
            dispatch({
                id: id,
                type: 'FETCH_INFO_FULFILLED',
                query: query,
                payload: response.data,
            });
        }).catch((err) => {
            dispatch({
                id: id,
                type: 'FETCH_INFO_REJECTED',
                query: query,
                payload: err,
            });
        });
    };
}

// TODO: Add Cancellation in case of long latency
export function fetchTimeline(similarityThreshold = 100, perspective = 'host', processID = null, id = null) {
    let link = 'phase/timeline';

    if (processID) {
        link = 'process/' + processID + '/' + link;
    }
    return function(dispatch) {
        dispatch({id: id, type: 'FETCH_TIMELINE'});
        axios.post(link, {
            similarityThreshold: similarityThreshold,
            timePerspective: perspective,
        }).then((response) => {
            dispatch({
                id: id,
                type: 'FETCH_TIMELINE_FULFILLED',
                payload: response.data,
                similarityThreshold: similarityThreshold,
            });
        }).catch((err) => {
            dispatch({
                id: id,
                type: 'FETCH_TIMELINE_REJECTED',
                payload: err,
                similarityThreshold: similarityThreshold,
            });
        });
    };
}

export function fetchTreemap(phaseID, similarityThreshold = 100, processID = null, id = null) {
    let link = 'phase/' + phaseID + '/treemap';

    if (processID) {
        link = 'process/' + processID + '/' + link;
    }
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({id: id, type: 'FETCH_TREEMAP_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({id: id, type: 'FETCH_TREEMAP_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function fetchCode(phaseID, similarityThreshold = 100, processID = null, id = null) {
    let link = 'phase/' + phaseID + '/codes';

    if (processID) {
        link = 'process/' + processID + '/' + link;
    }
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({id: id, type: 'FETCH_CODE_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({id: id, type: 'FETCH_CODE_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function fetchProf(phaseID, similarityThreshold = 100, processID = null, id = null) {
    let link = 'phase/' + phaseID + '/prof';

    if (processID) {
        link = 'process/' + processID + '/' + link;
    }
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({id: id, type: 'FETCH_PROF_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({id: id, type: 'FETCH_PROF_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function getPerfs(phaseID, similarityThreshold = 100, processID = null, id = null) {
    if (phaseID) {
        return [
            fetchTreemap(phaseID, similarityThreshold, processID, id),
            fetchCode(phaseID, similarityThreshold, processID, id),
            fetchProf(phaseID, similarityThreshold, processID, id),
        ];
    }
    return null;
}

export function setAppState(state, data) {
    return [
        {type: 'SET_APPSTATE', state: state, payload: data},
    ];
}
