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
    this.state = {data: []}
    this.pollInterval = props.pollInterval
    this.url = props.url
  }

  loadDataFromServer() {
    $.ajax({
      url: this.url,
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

  render() {
    if (this.state.data) {
      var buildNodes = this.state.data.map(function(build) {
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
    return (
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
