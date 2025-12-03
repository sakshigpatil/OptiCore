import React from 'react';

const Tasks = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Tasks</h1>
      </div>
      <div className="page-content">
        <div className="card">
          <div className="card-header">Assigned Tasks</div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Project</th>
                  <th>Priority</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Implement user authentication</td>
                  <td>HRMS Project</td>
                  <td><span style={{ color: '#e74c3c', fontWeight: 'bold' }}>High</span></td>
                  <td>2025-01-05</td>
                  <td><span style={{ color: '#f39c12', fontWeight: 'bold' }}>In Progress</span></td>
                  <td>
                    <button className="btn btn-success">Mark Complete</button>
                  </td>
                </tr>
                <tr>
                  <td>Fix UI bugs</td>
                  <td>HRMS Project</td>
                  <td><span style={{ color: '#f39c12', fontWeight: 'bold' }}>Medium</span></td>
                  <td>2025-01-08</td>
                  <td><span style={{ color: '#7f8c8d', fontWeight: 'bold' }}>Pending</span></td>
                  <td>
                    <button className="btn btn-primary">Start Task</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tasks;