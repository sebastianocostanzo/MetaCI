import React from 'react'
import ReactDOM from 'react-dom'


class BuildDetail extends React.Component {
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
      if (['error', 'fail'].includes(this.state.build.status)) {
        var buildErrorMessage = (
          <div className='slds-box slds-theme--warning slds-m-bottom--large'>
            <div className='slds-text-heading--large'>
              Build Exception: {this.state.build.exception}
            </div>
            <div className='slds-text-body--regular'>
              {this.state.build.error_message}
            </div>
          </div>
        )
      }
      var buildLog = (
        <div className='slds-box'>
          <div className='slds-text-heading--large sldes-m-bottom--medium'>
            Build Log
          </div>
          {this.state.build.log}
        </div>
      )
    }
    return (
      <div>
        {buildErrorMessage}
        {buildLog}
      </div>
    )
  }
}

ReactDOM.render(
  <BuildDetail
    buildId={buildId}
    poll_interval={1000}
  />,
  document.getElementById('container')
)
