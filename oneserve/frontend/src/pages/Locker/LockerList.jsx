import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FileText, Shield, CheckCircle } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const LockerList = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/locker/list');
      setDocuments(response.data);
    } catch (error) {
      toast.error('Error loading documents');
    } finally {
      setLoading(false);
    }
  };

  const getDocIcon = (type) => {
    return type === 'AADHAAR' || type === 'PAN' ? Shield : FileText;
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
          <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">DigiLocker</h1>
            <button onClick={() => navigate('/locker/upload')} className="btn-primary flex items-center space-x-2">
              <Plus className="h-5 w-5" />
              <span>Upload Document</span>
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-500">No documents uploaded yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {documents.map((doc) => {
                const Icon = getDocIcon(doc.doc_type);
                return (
                  <div key={doc.id} className="card hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="p-3 bg-primary-100 rounded-lg">
                        <Icon className="h-6 w-6 text-primary-600" />
                      </div>
                      {doc.verified && (
                        <CheckCircle className="h-5 w-5 text-success-600" />
                      )}
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">{doc.doc_type}</h3>
                    <p className="text-sm text-gray-600 mb-2">{doc.file_name}</p>
                    {doc.extracted_text && (
                      <p className="text-xs text-gray-500 line-clamp-2 mb-2">
                        {doc.extracted_text}
                      </p>
                    )}
                    <p className="text-xs text-gray-400">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default LockerList;
