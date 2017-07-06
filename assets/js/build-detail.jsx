import React from 'react'
import ReactDOM from 'react-dom'


class BuildDetail extends React.Component {
  constructor() {
    super()
    this.state = {data: {}}
  }

  loadDataFromServer() {
    $.ajax({
      url: `api/${this.props.buildId}?format=json`,
      datatype: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data})
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
    if (this.state.data) {
      if (['error', 'fail'].includes(this.state.data.status)) {
        var buildErrorMessage = (
          <div className='slds-box slds-theme--warning slds-m-bottom--large'>
            <h3 className='slds-text-heading--large'>
              Build Exception: {this.state.data.exception}
            </h3>
            <p>{this.state.data.error_message}</p>
          </div>
        )
      }
      var buildLog = (
        <div className='slds-box'>
          <h3 className='slds-text-heading--large sldes-m-bottom--medium'>
            Build Log
          </h3>
          {this.state.data.log}
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
