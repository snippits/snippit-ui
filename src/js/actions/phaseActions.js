import axios from 'axios';

export function setSimilarityThreshold(similarity_threshold) {
  return {
      type: 'SET_SIMILARITY_THRESHOLD',
      payload: similarity_threshold,
    };
}

// TODO: Add Cancellation in case of long latency
export function fetchTimeline(similarity_threshold) {
  var link = 'output/phase-history-' + (similarity_threshold / 10) + '.json?_=' + new Date().getTime();

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

export function fetchTreemap(phase_id) {
  var link = 'output/phase-treemap-' + phase_id + '?_=' + new Date().getTime();
  return function(dispatch) {
      axios.get(link)
          .then((response) => {
              dispatch({type: 'FETCH_TREEMAP_FULFILLED', payload: response.data});
            })
          .catch((err) => {
              dispatch({type: 'FETCH_TREEMAP_REJECTED', payload: err});
            });
    };
}

export function fetchCode(phase_id) {
  var link = 'output/phase-code-' + phase_id + '?_=' + new Date().getTime();
  return function(dispatch) {
      axios.get(link)
          .then((response) => {
              dispatch({type: 'FETCH_CODE_FULFILLED', payload: response.data});
            })
          .catch((err) => {
              dispatch({type: 'FETCH_CODE_REJECTED', payload: err});
            });
    };
}

export function fetchProf(phase_id) {
  var link = 'output/phase-prof-' + phase_id + '?_=' + new Date().getTime();
  return function(dispatch) {
      axios.get(link)
          .then((response) => {
              dispatch({type: 'FETCH_PROF_FULFILLED', payload: response.data});
            })
          .catch((err) => {
              dispatch({type: 'FETCH_PROF_REJECTED', payload: err});
            });
    };
}

export function setSelectedPhase(phase_id) {
  if (phase_id) {
    return [{
        type: 'SET_SELECTED_PHASE_ID',
        payload: phase_id,
      },
        fetchTreemap(phase_id),
        fetchCode(phase_id),
        fetchProf(phase_id),
    ];
  }
  return null;
}
