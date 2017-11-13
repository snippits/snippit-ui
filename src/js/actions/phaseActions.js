import axios from 'axios';

// TODO: Add Cancellation in case of long latency
export function fetchTimeline(similarityThreshold = 100, perspective = 'host') {
    let link = 'phase/timeline';

    console.log(link);
    return function(dispatch) {
        dispatch({type: 'FETCH_TIMELINE'});
        axios.post(link, {
            similarityThreshold: similarityThreshold,
            timePerspective: perspective,
        }).then((response) => {
            dispatch({
                type: 'FETCH_TIMELINE_FULFILLED',
                payload: response.data,
                similarityThreshold: similarityThreshold,
            });
        }).catch((err) => {
            dispatch({
                type: 'FETCH_TIMELINE_REJECTED',
                payload: err,
                similarityThreshold: similarityThreshold,
            });
        });
    };
}

export function fetchTreemap(phaseID, similarityThreshold = 100) {
    let link = 'phase/' + phaseID + '/treemap';
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({type: 'FETCH_TREEMAP_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({type: 'FETCH_TREEMAP_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function fetchCode(phaseID, similarityThreshold = 100) {
    let link = 'phase/' + phaseID + '/codes';
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({type: 'FETCH_CODE_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({type: 'FETCH_CODE_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function fetchProf(phaseID, similarityThreshold = 100) {
    let link = 'phase/' + phaseID + '/prof';
    return function(dispatch) {
        axios.post(link, {
            similarityThreshold: similarityThreshold,
        }).then((response) => {
            dispatch({type: 'FETCH_PROF_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({type: 'FETCH_PROF_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function setSelectedPhase(phaseID, similarityThreshold = 100) {
    if (phaseID) {
        return [
            fetchTreemap(phaseID, similarityThreshold),
            fetchCode(phaseID, similarityThreshold),
            fetchProf(phaseID, similarityThreshold),
        ];
    }
    return null;
}
