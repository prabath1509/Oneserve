import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Folder, FileText } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const CertificateApply = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [formData, setFormData] = useState({
    certificate_type: 'Income Certificate',
    applicant_name: '',
    father_name: '',
    mother_name: '',
    date_of_birth: '',
    address: '',
    purpose: '',
  });
  const [documents, setDocuments] = useState([]);
  const [lockerDocuments, setLockerDocuments] = useState([]);
  const [selectedLockerDocs, setSelectedLockerDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingLockerDocs, setLoadingLockerDocs] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLockerDocuments();
  }, []);

  const fetchLockerDocuments = async () => {
    setLoadingLockerDocs(true);
    try {
      const response = await api.get('/locker/list');
      setLockerDocuments(response.data);
    } catch (error) {
      console.error('Error fetching locker documents:', error);
    } finally {
      setLoadingLockerDocs(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const toggleLockerDoc = (docId) => {
    setSelectedLockerDocs(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = new FormData();
      Object.keys(formData).forEach(key => {
        data.append(key, formData[key]);
      });
      
      // Add uploaded documents
      documents.forEach(doc => {
        data.append('documents', doc);
      });

      // Add selected locker document IDs
      if (selectedLockerDocs.length > 0) {
        data.append('locker_doc_ids', selectedLockerDocs.join(','));
      }

      await api.post('/certificates/apply', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Application submitted successfully!');
      navigate('/certificates');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error submitting application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Apply for Certificate</h1>
              <p className="text-gray-600 mt-1">Fill in the details and attach supporting documents</p>
            </div>

            <div className="card">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Certificate Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Certificate Type *
                  </label>
                  <select
                    name="certificate_type"
                    value={formData.certificate_type}
                    onChange={handleChange}
                    className="input-field"
                    required
                  >
                    <option>Income Certificate</option>
                    <option>Domicile Certificate</option>
                    <option>Birth Certificate</option>
                    <option>Caste Certificate</option>
                  </select>
                </div>

                {/* Applicant Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Applicant Name *
                  </label>
                  <input
                    type="text"
                    name="applicant_name"
                    value={formData.applicant_name}
                    onChange={handleChange}
                    className="input-field"
                    required
                  />
                </div>

                {/* Father's and Mother's Name */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Father&apos;s Name
                    </label>
                    <input
                      type="text"
                      name="father_name"
                      value={formData.father_name}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Mother&apos;s Name
                    </label>
                    <input
                      type="text"
                      name="mother_name"
                      value={formData.mother_name}
                      onChange={handleChange}
                      className="input-field"
                    />
                  </div>
                </div>

                {/* Date of Birth */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    name="date_of_birth"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    className="input-field"
                  />
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Address
                  </label>
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    rows={3}
                    className="input-field"
                  />
                </div>

                {/* Purpose */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Purpose
                  </label>
                  <input
                    type="text"
                    name="purpose"
                    value={formData.purpose}
                    onChange={handleChange}
                    className="input-field"
                    placeholder="e.g., Bank loan, School admission"
                  />
                </div>

                {/* Supporting Documents Section */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Supporting Documents
                  </h3>

                  {/* Upload New Documents */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Upload className="inline h-4 w-4 mr-1" />
                      Upload New Documents
                    </label>
                    <input
                      type="file"
                      multiple
                      onChange={(e) => setDocuments(Array.from(e.target.files))}
                      className="input-field"
                      accept=".pdf,.jpg,.jpeg,.png"
                    />
                    {documents.length > 0 && (
                      <p className="text-sm text-success-600 mt-2">
                        ✓ {documents.length} file(s) selected
                      </p>
                    )}
                  </div>

                  {/* Select from DigiLocker */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      <Folder className="inline h-4 w-4 mr-1" />
                      Select from DigiLocker
                    </label>

                    {loadingLockerDocs ? (
                      <div className="text-center py-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                      </div>
                    ) : lockerDocuments.length === 0 ? (
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                        <FileText className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">
                          No documents in DigiLocker
                        </p>
                        <button
                          type="button"
                          onClick={() => navigate('/locker/upload')}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium mt-2"
                        >
                          Upload documents →
                        </button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto p-2 border border-gray-200 rounded-lg">
                        {lockerDocuments.map((doc) => (
                          <label
                            key={doc.id}
                            className={`flex items-start space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                              selectedLockerDocs.includes(doc.id)
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-200 hover:border-gray-300 bg-white'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={selectedLockerDocs.includes(doc.id)}
                              onChange={() => toggleLockerDoc(doc.id)}
                              className="mt-1"
                            />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {doc.file_name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {doc.doc_type}
                                {doc.verified && (
                                  <span className="ml-2 text-success-600">✓ Verified</span>
                                )}
                              </p>
                            </div>
                          </label>
                        ))}
                      </div>
                    )}

                    {selectedLockerDocs.length > 0 && (
                      <p className="text-sm text-primary-600 mt-2">
                        ✓ {selectedLockerDocs.length} document(s) selected from DigiLocker
                      </p>
                    )}
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex space-x-4 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Submitting...' : 'Submit Application'}
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate('/certificates')}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default CertificateApply;
