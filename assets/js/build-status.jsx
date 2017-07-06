import React from 'react'
import ReactDOM from 'react-dom'
import * as utils from './utils.js'

class BuildStatus extends React.Component {
  constructor() {
    super()
    this.state = {build: null}
  }

  loadDataFromServer() {
    $.ajax({
      url: `api/${this.props.buildId}?format=json`,
      datatype: 'json',
      cache: false,
      success: function(data) {
        this.setState({build: data})
      }.bind(this)
    })
  }

  componentDidMount() {
    this.loadDataFromServer()
    this.timerID = setInterval(
      this.loadDataFromServer.bind(this),
      this.props.poll_interval
    )
  }

  componentWillUnmount() {
    clearInterval(this.timerID)
  }

  render() {
    if (this.state.build) {
      return (
        <div className='slds-text-body--regular slds-truncate' title={this.state.build.status}>
          <div className={`slds-badge ${utils.getClassForStatus(this.state.build.status)}`}>
            {this.state.build.status}
          </div>
        </div>
      )
    } else {return (<div></div>)}
  }
}

ReactDOM.render(
  <BuildStatus
    buildId={buildId}
    poll_interval={1000}
  />,
  document.getElementById('buildStatus')
)
