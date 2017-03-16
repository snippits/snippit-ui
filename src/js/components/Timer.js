import React from "react";
import {observer} from "mobx-react"
import {observable} from "mobx"

@observer class Timer extends React.Component {
    @observable secondsPassed = 0

    componentWillMount() {
        setInterval(() => {
            this.secondsPassed++;
            console.log(111);
        }, 1000)
    }

    render() {
        return (<span>Seconds passed: { this.secondsPassed } </span> )
    }
}


React.render(<Timer />, document.body)

export default Timer

