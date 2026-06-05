import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Filter } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const ComplaintList = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const { user } = useAuth();
  const navigate = useNavigate();
  const isOfficer = user?.role?.startsWith('OFFICER_');

  useEffect(() => {
    fetchComplaints();
  }, []);

  const fetchComplaints = async () => {
    try {
      const endpoint = isOfficer ? '/complaints/assigned' : '/complaints/my';
      const response = await api.get(endpoint);
      setComplaints(response.data);
    } catch (error) {
      toast.error('Error loading complaints');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      IN_PROGRESS: 'bg-blue-100 text-blue-800',
      RESOLVED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const filteredComplaints = filter === 'ALL' 
    ? complaints 
    : complaints.filter(c => c.status === filter);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {isOfficer ? 'Assigned Complaints' : 'My Complaints'}
              </h1>
              <p className="text-gray-600 mt-1">{filteredComplaints.length} total</p>
            </div>
            {!isOfficer && (
              <button
                onClick={() => navigate('/complaints/create')}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus className="h-5 w-5" />
                <span>New Complaint</span>
              </button>
            )}
          </div>

          <div className="mb-6 flex items-center space-x-4">
            <Filter className="h-5 w-5 text-gray-600" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input-field w-48"
            >
              <option value="ALL">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>

          {filteredComplaints.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-500">No complaints found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {filteredComplaints.map((complaint) => (
                <div
                  key={complaint.id}
                  onClick={() => navigate(`/complaints/${complaint.id}`)}
                  className="card hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {complaint.title || `Complaint #${complaint.id}`}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(complaint.status)}`}>
                          {complaint.status.replace('_', ' ')}
                        </span>
                        <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">
                          {complaint.category}
                        </span>
                      </div>
                      {complaint.description && (
                        <p className="text-gray-600 mb-2 line-clamp-2">{complaint.description}</p>
                      )}
                      {complaint.place && (
                        <p className="text-sm text-gray-500">📍 {complaint.place}</p>
                      )}
                      <p className="text-sm text-gray-500 mt-2">
                        Created: {new Date(complaint.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    {complaint.image_path && (
                      <div className="ml-4">
                        <img
                          src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/files/complaints/${complaint.image_path.split('/').pop()}`}
                          alt="Complaint"
                          className="w-24 h-24 rounded-lg object-cover border border-gray-200"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ComplaintList;
