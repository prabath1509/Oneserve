import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const ComplaintDetails = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState('');
  const [comment, setComment] = useState('');
  const [resolutionProof, setResolutionProof] = useState(null);
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const isOfficer = user?.role?.startsWith('OFFICER_');

  useEffect(() => {
    fetchComplaintDetails();
  }, [id]);

  const fetchComplaintDetails = async () => {
    try {
      const response = await api.get(`/complaints/${id}`);
      setComplaint(response.data);
      setNewStatus(response.data.status);
    } catch (error) {
      toast.error('Error loading complaint details');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    try {
      const data = new FormData();
      data.append('status', newStatus);
      if (resolutionProof) {
        data.append('resolution_proof', resolutionProof);
      }

      const response = await api.patch(`/complaints/${id}/status`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Status updated successfully');
      // Update local state with new data
      setComplaint(response.data);
      setNewStatus(response.data.status);
      setResolutionProof(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error updating status');
    }
  };

  const handleAddComment = async () => {
    if (!comment.trim()) return;

    try {
      await api.post(`/complaints/${id}/comment`, { comment });
      toast.success('Comment added');
      setComment('');
      fetchComplaintDetails();
    } catch (error) {
      toast.error('Error adding comment');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      IN_PROGRESS: 'bg-blue-100 text-blue-800',
      RESOLVED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back
          </button>

          <div className="max-w-4xl mx-auto space-y-6">
            <div className="card">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {complaint.title || `Complaint #${complaint.id}`}
                  </h1>
                  <p className="text-gray-500 text-sm mt-1">
                    Filed on {new Date(complaint.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex flex-col space-y-2 items-end">
                  <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(complaint.status)}`}>
                    {complaint.status.replace('_', ' ')}
                  </span>
                  <span className="px-4 py-2 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                    {complaint.category}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {complaint.description && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-700">{complaint.description}</p>
                  </div>
                )}

                {complaint.place && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Location</h3>
                    <p className="text-gray-700">📍 {complaint.place}</p>
                  </div>
                )}

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Citizen</h3>
                  <p className="text-gray-700">{complaint.citizen.full_name} ({complaint.citizen.email})</p>
                </div>

                {complaint.assigned_officer && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Assigned Officer</h3>
                    <p className="text-gray-700">{complaint.assigned_officer.full_name}</p>
                  </div>
                )}

                {complaint.image_path && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Complaint Image</h3>
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/complaints/${complaint.image_path.split('/').pop()}`}
                      alt="Complaint"
                      className="w-full max-w-md rounded-lg border-2 border-gray-200 shadow-sm"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%" y="50%" text-anchor="middle" dy=".3em"%3EImage not found%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  </div>
                )}

                {complaint.resolution_proof && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Resolution Proof</h3>
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/complaints/${complaint.resolution_proof.split('/').pop()}`}
                      alt="Resolution Proof"
                      className="w-full max-w-md rounded-lg border-2 border-green-200 shadow-sm"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%" y="50%" text-anchor="middle" dy=".3em"%3EImage not found%3C/text%3E%3C/svg%3E';
                      }}
                    />
                  </div>
                )}
              </div>
            </div>

            {isOfficer && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Update Status</h3>
                <div className="space-y-4">
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="input-field"
                  >
                    <option value="PENDING">Pending</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="RESOLVED">Resolved</option>
                    <option value="REJECTED">Rejected</option>
                  </select>

                  {newStatus === 'RESOLVED' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Resolution Proof (Optional)
                      </label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setResolutionProof(e.target.files[0])}
                        className="input-field"
                      />
                    </div>
                  )}

                  <button onClick={handleStatusUpdate} className="btn-primary">
                    Update Status
                  </button>
                </div>
              </div>
            )}

            {isOfficer && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Comment</h3>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                  className="input-field mb-4"
                  placeholder="Add your comment..."
                />
                <button onClick={handleAddComment} className="btn-primary">
                  Add Comment
                </button>
              </div>
            )}

            {complaint.comments && complaint.comments.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Comments</h3>
                <div className="space-y-4">
                  {complaint.comments.map((c) => (
                    <div key={c.id} className="border-l-4 border-primary-500 pl-4 py-2">
                      <p className="text-gray-700">{c.comment}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {c.officer.full_name} - {new Date(c.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ComplaintDetails;
