import React from 'react'
import ReactDOM from 'react-dom'

class BuildRebuild extends React.Component {
  constructor() {
    super()
    this.state = {build: null}
  }

  loadDataFromServer() {
    $.ajax({
      url: `/builds/api/${this.props.buildId}?format=json`,
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
    if (this.state.build && ['error', 'fail'].includes(this.state.build.status)) {
      return (
        <div className='slds-button-group' role='group'>
          <a href={`/builds/${this.props.buildId}/rebuild`}>
            <button className='slds-button slds-button--neutral'>
              Rebuild
            </button>
          </a>
        </div>
      )
    } else {return (<div></div>)}
  }
}

ReactDOM.render(
  <BuildRebuild
    buildId={buildId}
    poll_interval={1000}
  />,
  document.getElementById('buildRebuild')
)
