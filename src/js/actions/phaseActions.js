import axios from 'axios';

export function setSimilarityThreshold(similarityThreshold) {
    return {
        type: 'SET_SIMILARITY_THRESHOLD',
        payload: similarityThreshold,
    };
}

// TODO: Add Cancellation in case of long latency
export function fetchTimeline(similarityThreshold) {
    let link = 'output/phase-history-' + (similarityThreshold / 10) + '.json?_=' + new Date().getTime();

    console.log(link);
    return function(dispatch) {
        dispatch({type: 'FETCH_TIMELINE'});
        axios.get(link)
            .then((response) => {
                dispatch({type: 'FETCH_TIMELINE_FULFILLED', payload: response.data});
            })
            .catch((err) => {
                dispatch({type: 'FETCH_TIMELINE_REJECTED', payload: err});
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
    let link = 'output/phase-code-' + phaseID + '?_=' + new Date().getTime();
    return function(dispatch) {
        axios.get(link)
            .then((response) => {
                dispatch({type: 'FETCH_CODE_FULFILLED', payload: response.data, phaseID: phaseID});
            })
            .catch((err) => {
                dispatch({type: 'FETCH_CODE_REJECTED', payload: err, phaseID: phaseID});
            });
    };
}

export function fetchProf(phaseID) {
    let link = 'output/phase-prof-' + phaseID + '?_=' + new Date().getTime();
    return function(dispatch) {
        axios.get(link)
            .then((response) => {
                dispatch({type: 'FETCH_PROF_FULFILLED', payload: response.data, phaseID: phaseID});
            })
            .catch((err) => {
                dispatch({type: 'FETCH_PROF_REJECTED', payload: err, phaseID: phaseID});
            });
    };
}

export function setSelectedPhase(phaseID) {
    if (phaseID) {
        return [{
            type: 'SET_SELECTED_PHASE_ID',
            payload: phaseID,
        },
        fetchTreemap(phaseID),
        fetchCode(phaseID),
        fetchProf(phaseID),
        ];
    }
    return null;
}
