import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CreditCard, File } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const LockerUpload = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [step, setStep] = useState(1); // 1: select type, 2: upload file
  const [selectedType, setSelectedType] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractedText, setExtractedText] = useState('');
  const navigate = useNavigate();

  const documentTypes = [
    { 
      type: 'AADHAAR', 
      label: 'Aadhaar Card', 
      icon: CreditCard,
      color: 'bg-blue-50 border-blue-200 hover:bg-blue-100',
      iconColor: 'text-blue-600'
    },
    { 
      type: 'PAN', 
      label: 'PAN Card', 
      icon: CreditCard,
      color: 'bg-green-50 border-green-200 hover:bg-green-100',
      iconColor: 'text-green-600'
    },
    { 
      type: 'VOTER_ID', 
      label: 'Voter ID', 
      icon: CreditCard,
      color: 'bg-purple-50 border-purple-200 hover:bg-purple-100',
      iconColor: 'text-purple-600'
    },
    { 
      type: 'OTHER', 
      label: 'Other Document', 
      icon: File,
      color: 'bg-gray-50 border-gray-200 hover:bg-gray-100',
      iconColor: 'text-gray-600'
    },
  ];

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', selectedType);

      const response = await api.post('/locker/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.extracted_text) {
        setExtractedText(response.data.extracted_text);
      }

      toast.success('Document uploaded and verified successfully!');
      navigate('/locker');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Error uploading document';
      toast.error(errorMsg);
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
              <h1 className="text-3xl font-bold text-gray-900">Upload Document to DigiLocker</h1>
              <p className="text-gray-600 mt-1">
                {step === 1 ? 'Select document type' : `Upload your ${documentTypes.find(d => d.type === selectedType)?.label}`}
              </p>
            </div>

            {step === 1 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {documentTypes.map((docType) => {
                  const Icon = docType.icon;
                  return (
                    <button
                      key={docType.type}
                      onClick={() => handleTypeSelect(docType.type)}
                      className={`card ${docType.color} border-2 p-8 text-left transition-all hover:shadow-lg`}
                    >
                      <Icon className={`h-12 w-12 ${docType.iconColor} mb-4`} />
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {docType.label}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {docType.type === 'AADHAAR' && 'Upload your Aadhaar card for verification'}
                        {docType.type === 'PAN' && 'Upload your PAN card for verification'}
                        {docType.type === 'VOTER_ID' && 'Upload your Voter ID for verification'}
                        {docType.type === 'OTHER' && 'Upload any other document'}
                      </p>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="card">
                <div className="mb-6">
                  <button
                    onClick={() => {
                      setStep(1);
                      setFile(null);
                      setSelectedType('');
                    }}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    ← Change document type
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-400 transition-colors">
                    <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <input
                      type="file"
                      onChange={(e) => setFile(e.target.files[0])}
                      className="hidden"
                      id="file-upload"
                      accept="image/*,.pdf,.doc,.docx"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-primary-600 hover:text-primary-700 font-medium">
                        Choose file
                      </span>
                      <span className="text-gray-600"> or drag and drop</span>
                    </label>
                    <p className="text-xs text-gray-500 mt-2">
                      PNG, JPG, PDF, DOC up to 10MB
                    </p>
                    {file && (
                      <div className="mt-4 p-4 bg-green-50 rounded-lg">
                        <p className="text-sm text-success-600 font-medium">
                          ✓ Selected: {file.name}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                    <div className="flex">
                      <FileText className="h-5 w-5 text-yellow-400" />
                      <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                          <strong>Note:</strong> Your document will be automatically verified
                          {selectedType === 'AADHAAR' && ' Please ensure your Aadhaar number is clearly visible.'}
                          {selectedType === 'PAN' && ' Please ensure your PAN number is clearly visible.'}
                          {selectedType === 'VOTER_ID' && ' Please ensure your Voter ID details are clearly visible.'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {extractedText && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="text-sm font-semibold text-blue-900 mb-2">Extracted Text:</h4>
                      <p className="text-xs text-blue-800 whitespace-pre-wrap">{extractedText}</p>
                    </div>
                  )}

                  <div className="flex space-x-4">
                    <button 
                      type="submit" 
                      disabled={loading || !file} 
                      className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Uploading & Verifying...' : 'Upload Document'}
                    </button>
                    <button
                      type="button"
                      onClick={() => navigate('/locker')}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default LockerUpload;
