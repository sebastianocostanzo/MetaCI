import React from 'react'
import ReactDOM from 'react-dom'

function getSldsClassForStatus(status) {
  var s = 'slds-truncate slds-badge '
  switch(status) {
    case 'fail':
    case 'error':
      s += 'slds-theme--error'
      break
    case 'success':
      s += 'slds-theme--success'
      break
  }
  return s
}

class BuildsList extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      data: [],
      url: props.url
    }
    this.pollInterval = props.pollInterval
  }

  loadDataFromServer() {
    $.ajax({
      url: this.state.url,
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
      this.pollInterval
    )
  }

  componentWillUnmount() {
    clearInterval(this.timerID)
  }

  pagePrevious() {
    this.setState({url: this.state.data.previous})
  }

  pageNext() {
    this.setState({url: this.state.data.next})
  }

  render() {
    if (this.state.data.results) {
      var buildNodes = this.state.data.results.map(function(build) {
        return (
          <tr key={build.id}>
            <th data-label='Build Number'>
              <div className='slds-truncate' title={build.id}>
                <a href={`/builds/${build.id}`}>{build.id}</a>
              </div>
            </th>
            <td data-label='Status'>
              <div className={getSldsClassForStatus(build.status)} title={build.status}>
                <a href={`/builds/${build.id}`}>{build.status}</a>
              </div>
            </td>
            <td data-label='Repository'>
              <div className='slds-truncate' title={build.repo.name}>
                {build.repo.name}
              </div>
            </td>
            <td data-label='Plan'>
              <div className='slds-truncate' title={build.plan.name}>
                {build.plan.name}
              </div>
            </td>
            <td data-label='Branch'>
              <div className='slds-truncate' title={build.branch.name}>
                {build.branch.name}
              </div>
            </td>
            <td data-label='Commit'>
              <div className='slds-truncate' title={build.commit}>
                {build.commit}
              </div>
            </td>
            <td data-label='Start Date'>
              <div className='slds-truncate' title={build.time_start}>
                {build.time_start}
              </div>
            </td>
            <td data-label='End Date'>
              <div className='slds-truncate' title={build.time_end}>
                {build.time_end}
              </div>
            </td>
          </tr>
        )
      })
    }
    if (this.state.data.previous) {
      var pagePrevious = (
        <button
          className='slds-button slds-button--neutral'
          onClick={this.pagePrevious.bind(this)}>
          Previous
        </button>
      )
    }
    if (this.state.data.next) {
      var pageNext = (
        <button
          className='slds-button slds-button--neutral'
          onClick={this.pageNext.bind(this)}>
          Next
        </button>
      )
    }
    return (
      <div>
        <table className='slds-table slds-table--bordered slds-table--cell-buffer'>
          <thead>
            <tr className='slds-text-title--caps'>
              <th scope='col'>
                <div className='slds-truncate' title=''>#</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Status</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Repo</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Plan</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Branch/Tag</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Commit</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>Start Date</div>
              </th>
              <th scope='col'>
                <div className='slds-truncate' title=''>End Date</div>
              </th>
            </tr>
          </thead>
          <tbody>
            {buildNodes}
          </tbody>
        </table>
        <div className='slds-button-group slds-m-top--medium' role='group'>
          {pagePrevious}
          {pageNext}
        </div>
      </div>
    )
  }
}

ReactDOM.render(
  <BuildsList
    url='/builds/api/all?format=json'
    pollInterval={1000}
  />,
  document.getElementById('container')
)
