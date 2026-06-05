import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const CertificateDetails = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const fetchDetails = async () => {
    try {
      const response = await api.get(`/certificates/${id}`);
      setApplication(response.data);
    } catch (error) {
      toast.error('Error loading details');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await api.get(`/certificates/${id}/download`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Certificate downloaded');
    } catch (error) {
      toast.error('Error downloading certificate');
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
          <button onClick={() => navigate(-1)} className="mb-4 flex items-center text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back
          </button>

          <div className="max-w-3xl mx-auto card">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">{application.certificate_type}</h1>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Application ID</p>
                  <p className="font-semibold">#{application.id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-semibold">{application.status.replace('_', ' ')}</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500">Applicant Name</p>
                <p className="font-semibold">{application.applicant_name}</p>
              </div>

              {application.father_name && (
                <div>
                  <p className="text-sm text-gray-500">Father's Name</p>
                  <p className="font-semibold">{application.father_name}</p>
                </div>
              )}

              {application.date_of_birth && (
                <div>
                  <p className="text-sm text-gray-500">Date of Birth</p>
                  <p className="font-semibold">{application.date_of_birth}</p>
                </div>
              )}

              {application.address && (
                <div>
                  <p className="text-sm text-gray-500">Address</p>
                  <p className="font-semibold">{application.address}</p>
                </div>
              )}

              {application.rejection_reason && (
                <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                  <p className="text-sm text-red-600 font-medium">Rejection Reason:</p>
                  <p className="text-red-700">{application.rejection_reason}</p>
                </div>
              )}

              {application.status === 'CERTIFICATE_READY' && (
                <button onClick={handleDownload} className="btn-success flex items-center space-x-2">
                  <Download className="h-5 w-5" />
                  <span>Download Certificate</span>
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default CertificateDetails;
