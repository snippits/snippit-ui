import axios from 'axios';

// TODO: Add Cancellation in case of long latency
export function fetchTimeline(similarityThreshold) {
    let link = 'phase/timeline';

    console.log(link);
    return function(dispatch) {
        dispatch({type: 'FETCH_TIMELINE'});
        axios.post(link, {
            similarityThreshold: similarityThreshold,
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

export function fetchTreemap(phaseID) {
    let link = 'output/phase-treemap-' + phaseID + '?_=' + new Date().getTime();
    return function(dispatch) {
        axios.get(link)
            .then((response) => {
                dispatch({type: 'FETCH_TREEMAP_FULFILLED', payload: response.data, phaseID: phaseID});
            })
            .catch((err) => {
                dispatch({type: 'FETCH_TREEMAP_REJECTED', payload: err, phaseID: phaseID});
            });
    };
}

export function fetchCode(phaseID) {
    let link = 'phase/' + phaseID + '/codes';
    return function(dispatch) {
        axios.post(link, {
        }).then((response) => {
            dispatch({type: 'FETCH_CODE_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({type: 'FETCH_CODE_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function fetchProf(phaseID) {
    let link = 'phase/' + phaseID + '/prof';
    return function(dispatch) {
        axios.post(link, {
        }).then((response) => {
            dispatch({type: 'FETCH_PROF_FULFILLED', payload: response.data, phaseID: phaseID});
        }).catch((err) => {
            dispatch({type: 'FETCH_PROF_REJECTED', payload: err, phaseID: phaseID});
        });
    };
}

export function setSelectedPhase(phaseID) {
    if (phaseID) {
        return [
            fetchTreemap(phaseID),
            fetchCode(phaseID),
            fetchProf(phaseID),
        ];
    }
    return null;
}
