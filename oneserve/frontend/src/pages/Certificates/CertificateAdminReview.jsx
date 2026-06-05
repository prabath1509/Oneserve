import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const CertificateAdminReview = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);
  const [reason, setReason] = useState('');

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    try {
      const response = await api.get('/certificates/admin/pending');
      setApplications(response.data);
    } catch (error) {
      toast.error('Error loading applications');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await api.patch(`/certificates/${id}/approve`, { approved: true });
      toast.success('Application approved');
      fetchPending();
      setSelectedApp(null);
    } catch (error) {
      toast.error('Error approving application');
    }
  };

  const handleReject = async (id) => {
    if (!reason.trim()) {
      toast.error('Please provide a reason');
      return;
    }
    try {
      await api.patch(`/certificates/${id}/approve`, { approved: false, reason });
      toast.success('Application rejected');
      fetchPending();
      setSelectedApp(null);
      setReason('');
    } catch (error) {
      toast.error('Error rejecting application');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 p-6 lg:p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Certificate Review</h1>

          {applications.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-500">No pending applications</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {applications.map((app) => (
                <div key={app.id} className="card">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{app.certificate_type}</h3>
                      <p className="text-gray-600">Applicant: {app.applicant_name}</p>
                      <p className="text-sm text-gray-500">Applied: {new Date(app.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {selectedApp === app.id && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Rejection Reason (if rejecting)
                        </label>
                        <textarea
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                          rows={3}
                          className="input-field"
                          placeholder="Enter reason for rejection..."
                        />
                      </div>
                      <div className="flex space-x-4">
                        <button onClick={() => handleApprove(app.id)} className="btn-success">
                          Approve
                        </button>
                        <button onClick={() => handleReject(app.id)} className="btn-danger">
                          Reject
                        </button>
                        <button onClick={() => {setSelectedApp(null); setReason('');}} className="btn-secondary">
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  {!selectedApp && (
                    <div className="flex space-x-4 mt-4">
                      <button 
                        onClick={() => navigate(`/admin/certificates/${app.id}`)} 
                        className="btn-primary flex-1"
                      >
                        View Full Details & Review
                      </button>
                      <button 
                        onClick={() => setSelectedApp(app.id)} 
                        className="btn-secondary"
                      >
                        Quick Approve/Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default CertificateAdminReview;
