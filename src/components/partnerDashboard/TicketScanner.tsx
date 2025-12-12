import { QrCode, Check, X, Clock, Calendar, User, Ticket } from 'lucide-react';
import { useState } from 'react';

export default function TicketScanner() {
  const [scanResult, setScanResult] = useState<{
    status: 'success' | 'error' | 'used' | null;
    ticket?: {
      ticketId: string;
      eventName: string;
      attendeeName: string;
      ticketType: string;
      purchaseDate: string;
    };
  }>({ status: null });

  const [scanHistory, setScanHistory] = useState([
    {
      id: 1,
      ticketId: 'TKT-2024-001',
      attendeeName: 'John Kamau',
      eventName: 'Summer Music Festival',
      ticketType: 'VIP',
      scanTime: '2024-06-15 14:30',
      status: 'Valid'
    },
    {
      id: 2,
      ticketId: 'TKT-2024-002',
      attendeeName: 'Sarah Muthoni',
      eventName: 'Summer Music Festival',
      ticketType: 'Regular',
      scanTime: '2024-06-15 14:32',
      status: 'Valid'
    },
    {
      id: 3,
      ticketId: 'TKT-2024-003',
      attendeeName: 'David Ochieng',
      eventName: 'Summer Music Festival',
      ticketType: 'VIP',
      scanTime: '2024-06-15 14:35',
      status: 'Already Used'
    }
  ]);

  const handleScan = () => {
    // Simulate scanning
    const mockTicket = {
      ticketId: 'TKT-2024-004',
      eventName: 'Summer Music Festival 2024',
      attendeeName: 'Mock User',
      ticketType: 'VIP',
      purchaseDate: '2024-06-10'
    };

    setScanResult({
      status: 'success',
      ticket: mockTicket
    });

    // Add to scan history
    const newScan = {
      id: scanHistory.length + 1,
      ticketId: mockTicket.ticketId,
      attendeeName: mockTicket.attendeeName,
      eventName: mockTicket.eventName,
      ticketType: mockTicket.ticketType,
      scanTime: new Date().toLocaleString(),
      status: 'Valid'
    };

    setScanHistory([newScan, ...scanHistory]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Ticket Scanner</h2>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Scan and validate event tickets
        </p>
      </div>

      {/* Scanner Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-8">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-32 h-32 bg-[#27aae2]/10 rounded-full mb-4">
              <QrCode className="w-16 h-16 text-[#27aae2]" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Ready to Scan
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Position the QR code within the frame to scan
            </p>
          </div>

          {/* Mock Scanner Frame */}
          <div className="relative bg-gray-900 rounded-xl overflow-hidden mb-6" style={{ aspectRatio: '1' }}>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-64 h-64 border-4 border-[#27aae2] rounded-lg opacity-50"></div>
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <QrCode className="w-32 h-32 text-gray-700" />
            </div>
          </div>

          {/* Test Scan Button */}
          <button
            onClick={handleScan}
            className="w-full bg-[#27aae2] text-white py-4 rounded-xl font-semibold hover:bg-[#1e8bc3] transition-all shadow-lg"
          >
            Simulate Scan
          </button>

          {/* Scan Result */}
          {scanResult.status && (
            <div className={`mt-6 p-6 rounded-xl ${
              scanResult.status === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 border-2 border-green-500'
                : scanResult.status === 'used'
                ? 'bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-500'
                : 'bg-red-50 dark:bg-red-900/20 border-2 border-red-500'
            }`}>
              <div className="flex items-center space-x-3 mb-4">
                {scanResult.status === 'success' ? (
                  <Check className="w-8 h-8 text-green-600 dark:text-green-400" />
                ) : scanResult.status === 'used' ? (
                  <Clock className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                ) : (
                  <X className="w-8 h-8 text-red-600 dark:text-red-400" />
                )}
                <h4 className={`text-xl font-bold ${
                  scanResult.status === 'success'
                    ? 'text-green-900 dark:text-green-100'
                    : scanResult.status === 'used'
                    ? 'text-orange-900 dark:text-orange-100'
                    : 'text-red-900 dark:text-red-100'
                }`}>
                  {scanResult.status === 'success'
                    ? 'Valid Ticket!'
                    : scanResult.status === 'used'
                    ? 'Already Used'
                    : 'Invalid Ticket'
                  }
                </h4>
              </div>

              {scanResult.ticket && (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
                    <Ticket className="w-4 h-4" />
                    <span className="font-semibold">{scanResult.ticket.ticketId}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
                    <Calendar className="w-4 h-4" />
                    <span>{scanResult.ticket.eventName}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
                    <User className="w-4 h-4" />
                    <span>{scanResult.ticket.attendeeName} - {scanResult.ticket.ticketType}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Scan History */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Scans
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Ticket ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Attendee
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Event
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Scan Time
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {scanHistory.map((scan) => (
                <tr key={scan.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                    {scan.ticketId}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {scan.attendeeName}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {scan.eventName}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      scan.ticketType === 'VIP'
                        ? 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200'
                        : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                    }`}>
                      {scan.ticketType}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {scan.scanTime}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      scan.status === 'Valid'
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                        : 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200'
                    }`}>
                      {scan.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
          Important Note
        </h4>
        <p className="text-gray-600 dark:text-gray-400 text-sm">
          Each ticket can only be scanned once. Already scanned tickets will be flagged automatically.
          Make sure to check the attendee's ID matches the ticket information.
        </p>
      </div>
    </div>
  );
}
