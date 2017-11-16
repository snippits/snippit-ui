import React from 'react';
import {connect} from 'react-redux';
import {round} from '../common.js';


const InstBreakdownBar = (props) => {
    const category = ['aluOp', 'bitOp', 'branch', 'load', 'store'];
    const colors = {
        'aluOp': 'progress-bar-danger',
        'bitOp': 'progress-bar-primary',
        'branch': 'progress-bar-success',
        'load': 'progress-bar-warning',
        'store': 'progress-bar-info',
    };
    const total = category.reduce((sum, name) => {
        if (props.inst[name]) return sum + props.inst[name];
        else return sum;
    }, 0);
    const ratioBreakdowns = [];
    for (let i = 0; i < category.length; i++) {
        const name = category[i];
        if (props.inst[name]) {
            ratioBreakdowns.push({
                name: name,
                color: colors[name],
                value: round(100 * (props.inst[name] / total)),
            });
        }
    }
    const fixVal = 100 - ratioBreakdowns.reduce((sum, item) => {
        return sum + item.value;
    }, 0);
    // Adjust the last element to ensure that total sum is exactly 100%
    ratioBreakdowns.slice(-1)[0].value += fixVal;
    return (
        <div className="progress" style={{margin: 0}}>
            {ratioBreakdowns.map( (ratio) =>
                <div key={ratio.name}
                    className={'progress-bar ' + ratio.color}
                    role='progressbar'
                    style={{width: ratio.value + '%'}}>
                    {ratio.name} ({ratio.value}%)
                </div>
            )}
        </div>
    );
};

const UserRatioBar = (props) => {
    const userRatio = round(100 * props.user / (props.user + props.system));
    const systemRatio = 100 - userRatio;
    const progressbarStyleUser = {
        width: userRatio + '%',
    };
    const progressbarStyleSystem = {
        width: systemRatio + '%',
    };
    const progressStyle = {
        margin: 0,
    };
    return (
        <div className="progress" style={progressStyle}>
            <div className="progress-bar progress-bar-success"
                role="progressbar"
                style={progressbarStyleUser}>
                User ({userRatio}%)
            </div>
            <div className="progress-bar progress-bar-danger"
                role="progressbar"
                style={progressbarStyleSystem}>
                System ({systemRatio}%)
            </div>
        </div>
    );
};

const CPUTableRow = (props) => {
    const {name} = props;
    const {counters} = props;
    return (
        <tr>
            <td>{name}</td>
            <td className='align-right'>{counters.total}</td>
            <td>
                <UserRatioBar user={counters.user} system={counters.system} />
            </td>
        </tr>
    );
};

const CPUTable = (props) => {
    const {value} = props;
    return (
        <table className='table table-hover'>
            <caption>CPU</caption>
            <tbody>
                <tr>
                    <th className='col-md-2'>Type</th>
                    <th className='col-md-3'># Accesses</th>
                    <th className='col-md-7'>Ratio</th>
                    <th></th>
                </tr>
                <CPUTableRow name='Instruction' counters={value.instruction} />
                <CPUTableRow name='Load' counters={value.load} />
                <CPUTableRow name='Store' counters={value.store} />
                <tr>
                    <td colSpan='3'>
                        <InstBreakdownBar inst={value.instruction} />
                    </td>
                </tr>
            </tbody>
        </table>
    );
};

const BranchTable = (props) => {
    const {value} = props;
    return (
        <table className='table table-hover'>
            <caption>Branch</caption>
            <tbody>
                <tr>
                    <th className='col-md-2'>Type</th>
                    <th className='col-md-3'># Accesses</th>
                    <th className='col-md-2'>Miss Rate</th>
                    <th className='col-md-2'># Hits</th>
                    <th className='col-md-2'># Misses</th>
                    <th></th>
                </tr>
                <tr>
                    <td>Summary</td>
                    <td className='align-right'>{value.hit + value.miss}</td>
                    <td className='align-right'>
                        {round((1.0 - value.accuracy) * 100, 2)}%
                    </td>
                    <td className='align-right'>{value.hit}</td>
                    <td className='align-right'>{value.miss}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    );
};

const CacheTableRaw = (props) => {
    const {name} = props;
    const {counters} = props;
    return (
        <tr>
            <td>{name}</td>
            <td className='align-right'>{counters.accessCount}</td>
            <td className='align-right'>
                {round(counters.missRate * 100, 2)}%
            </td>
            <td className='align-right'>{counters.readMiss}</td>
            <td className='align-right'>{counters.writeMiss}</td>
            <td></td>
        </tr>
    );
};

const CacheTable = (props) => {
    const {value} = props;
    return (
        <table className='table table-hover'>
            <caption>Cache</caption>
            <tbody>
                <tr>
                    <th className='col-md-2'>Level</th>
                    <th className='col-md-3'># Accesses</th>
                    <th className='col-md-2'>Miss Rate</th>
                    <th className='col-md-2'># Read Misses</th>
                    <th className='col-md-2'># Write Misses</th>
                    <th></th>
                </tr>
                <CacheTableRaw name='Level 2' counters={value.level2}/>
                <CacheTableRaw name='I Cache' counters={value.iCache}/>
                <CacheTableRaw name='D Cache' counters={value.dCache}/>
            </tbody>
        </table>
    );
};

const TimeTable = (props) => {
    const {value} = props;
    return (
        <table className='table table-hover'>
            <caption>
                Time (ms) - Wallclock time elapsed {round(value.host / 1e9, 3)} s
            </caption>
            <tbody>
                <tr>
                    <th className='col-md-1'>Target</th>
                    <th className='col-md-1'>CPU</th>
                    <th className='col-md-1'>Branch</th>
                    <th className='col-md-1'>Cache</th>
                    <th className='col-md-1'>Memory</th>
                    <th className='col-md-1'>IO</th>
                    <th></th>
                </tr>
                <tr>
                    <td className='align-right'>{round(value.target / 1e6, 3)}</td>
                    <td className='align-right'>{round(value.cpu / 1e6, 3)}</td>
                    <td className='align-right'>{round(value.branch / 1e6, 3)}</td>
                    <td className='align-right'>{round(value.cache / 1e6, 3)}</td>
                    <td className='align-right'>{round(value.systemMemory / 1e6, 3)}</td>
                    <td className='align-right'>{round(value.ioMemory / 1e6, 3)}</td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    );
};

@connect((store) => {
    return {
        prof: store.phase.prof,
    };
})
export default class ProfilingResult extends React.Component {
    constructor() {
        super();
    }

    componentDidMount() {
    }

    generateTable(counters) {
        const mips = round(1e3 * counters.instruction.total / counters.time.host, 2);
        if (typeof counters === 'string') {
            return counters;
        } else {
            return (
                <div>
                    <CPUTable value={counters} />
                    <BranchTable value={counters.branch} />
                    <CacheTable value={counters.cache}/>
                    <TimeTable value={counters.time}/>
                    <h4>Emulation speed: {mips} MIPS</h4>
                </div>
            );
        }
    }

    render() {
        const {prof} = this.props;
        console.log('ProfilingResult');

        let output = '';
        if (prof.error) {
            console.log('Cannot fetch the profiling counters');
        } else if (prof.fetched) {
            output = this.generateTable(prof.data);
        }

        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Profiling Result</h1>
                {output}
            </div>
        );
    }
}
