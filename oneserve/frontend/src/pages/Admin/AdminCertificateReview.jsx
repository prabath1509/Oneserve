import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../../api/axios";

export default function AdminCertificateReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchApplicationDetails();
  }, [id]);

  const fetchApplicationDetails = async () => {
    try {
      const response = await api.get(`/certificates/admin/${id}`);
      setApplication(response.data);
    } catch (error) {
      console.error('Error fetching application:', error);
      alert('Failed to load application details');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!comment.trim()) {
      alert('Please provide a comment before approving');
      return;
    }

    if (!confirm('Are you sure you want to approve this application?')) {
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('comment', comment);

      await api.patch(`/certificates/${id}/admin-approve`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert('Application approved successfully!');
      navigate('/admin/certificates');
    } catch (error) {
      console.error('Error approving application:', error);
      alert(error.response?.data?.detail || 'Failed to approve application');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!comment.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    if (!confirm('Are you sure you want to reject this application?')) {
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('comment', comment);

      await api.patch(`/certificates/${id}/admin-reject`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert('Application rejected successfully');
      navigate('/admin/certificates');
    } catch (error) {
      console.error('Error rejecting application:', error);
      alert(error.response?.data?.detail || 'Failed to reject application');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddNote = async () => {
    if (!comment.trim()) {
      alert('Please enter a note');
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('comment', comment);

      await api.post(`/certificates/${id}/admin-note`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      alert('Note added successfully');
      setComment('');
      fetchApplicationDetails(); // Refresh to show new note
    } catch (error) {
      console.error('Error adding note:', error);
      alert('Failed to add note');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'bg-yellow-100 text-yellow-800',
      'APPROVED': 'bg-green-100 text-green-800',
      'REJECTED': 'bg-red-100 text-red-800',
      'CERTIFICATE_READY': 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getActionColor = (action) => {
    const colors = {
      'APPROVED': 'text-green-600',
      'REJECTED': 'text-red-600',
      'NOTE': 'text-blue-600'
    };
    return colors[action] || 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Loading application details...</div>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">Application not found</div>
      </div>
    );
  }

  const formData = application.form_data ? JSON.parse(application.form_data) : {};
  const lockerDocIds = application.locker_doc_ids ? application.locker_doc_ids.split(',') : [];

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Header */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Certificate Application Review
                </h1>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>Application ID: #{application.id}</span>
                  <span>•</span>
                  <span>Type: {application.certificate_type}</span>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
                {application.status}
              </span>
            </div>
          </div>

          {/* Applicant Details */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Applicant Information</h2>
            </div>
            <div className="p-6 grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <p className="text-gray-900">{application.applicant.full_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <p className="text-gray-900">{application.applicant.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <p className="text-gray-900">{application.applicant.phone || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Application Date</label>
                <p className="text-gray-900">{new Date(application.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Application Form Data */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Application Details</h2>
            </div>
            <div className="p-6 grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Applicant Name</label>
                <p className="text-gray-900">{application.applicant_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Father's Name</label>
                <p className="text-gray-900">{application.father_name || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mother's Name</label>
                <p className="text-gray-900">{application.mother_name || 'N/A'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                <p className="text-gray-900">{application.date_of_birth || 'N/A'}</p>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <p className="text-gray-900">{application.address || 'N/A'}</p>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Purpose</label>
                <p className="text-gray-900">{application.purpose || 'N/A'}</p>
              </div>
              {application.additional_info && (
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Additional Information</label>
                  <p className="text-gray-900">{application.additional_info}</p>
                </div>
              )}
            </div>
          </div>

          {/* Uploaded Documents */}
          {application.documents && application.documents.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Uploaded Documents</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  {application.documents.map((doc) => (
                    <div key={doc.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">{doc.document_type}</h3>
                          <p className="text-sm text-gray-500">{doc.filename}</p>
                        </div>
                        {doc.is_verified && (
                          <span className="text-green-600 text-sm">✓ Verified</span>
                        )}
                      </div>
                      <a
                        href={`http://localhost:8000/files/certificates/${doc.filepath}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline"
                      >
                        View Document →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* DigiLocker Documents */}
          {lockerDocIds.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">DigiLocker Documents</h2>
              </div>
              <div className="p-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    Applicant linked {lockerDocIds.length} DigiLocker document(s) to this application.
                  </p>
                  <p className="text-xs text-blue-600 mt-2">
                    Document IDs: {lockerDocIds.join(', ')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Comments Timeline */}
          {application.comments && application.comments.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Review History</h2>
              </div>
              <div className="p-6 space-y-4">
                {application.comments.map((commentItem) => (
                  <div key={commentItem.id} className="border-l-4 border-gray-300 pl-4 py-2">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">{commentItem.admin.full_name}</span>
                        <span className={`text-sm font-medium ${getActionColor(commentItem.action)}`}>
                          {commentItem.action}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(commentItem.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-gray-700">{commentItem.comment}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Admin Action Panel */}
          {application.status === 'PENDING' && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Review Actions</h2>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Comment / Reason *
                  </label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows="4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your comment or reason for approval/rejection..."
                  />
                </div>
                <div className="flex space-x-4">
                  <button
                    onClick={handleApprove}
                    disabled={submitting || !comment.trim()}
                    className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                  >
                    {submitting ? 'Processing...' : 'Approve Application'}
                  </button>
                  <button
                    onClick={handleReject}
                    disabled={submitting || !comment.trim()}
                    className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                  >
                    {submitting ? 'Processing...' : 'Reject Application'}
                  </button>
                  <button
                    onClick={handleAddNote}
                    disabled={submitting || !comment.trim()}
                    className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                  >
                    {submitting ? 'Saving...' : 'Add Note Only'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Back Button */}
          <div className="flex justify-start">
            <button
              onClick={() => navigate('/admin/certificates')}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              ← Back to Applications
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
