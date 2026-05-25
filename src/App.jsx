
import React, { useEffect, useMemo, useState } from 'react';
import Papa from 'papaparse';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line } from 'recharts';
import { Search, Download, MessageCircle, Users, BarChart3, Filter } from 'lucide-react';
import './styles.css';

const SENTIMENT_COLORS = { Positif: '#16a34a', Netral: '#64748b', Negatif: '#dc2626' };
const PLATFORM_COLORS = { YouTube: '#ef4444', Facebook: '#2563eb' };

function normalizeNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function toCsv(rows) {
  return Papa.unparse(rows);
}

function downloadCsv(rows, filename) {
  const blob = new Blob([toCsv(rows)], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function countBy(rows, key) {
  const map = new Map();
  rows.forEach((row) => {
    const value = row[key] || 'Tidak diketahui';
    map.set(value, (map.get(value) || 0) + 1);
  });
  return Array.from(map.entries()).map(([name, value]) => ({ name, value }));
}

function topAuthors(rows) {
  const map = new Map();
  rows.forEach((row) => {
    const key = row.Author || 'Anonim';
    map.set(key, (map.get(key) || 0) + 1);
  });
  return Array.from(map.entries())
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);
}

function topWords(rows) {
  const stopwords = new Set(['yang','dan','di','ke','dari','ini','itu','untuk','dengan','ada','atau','karena','pada','dalam','juga','saya','kita','mereka','tidak','jadi','lebih','akan','nya','ya','kok','kan','the','of','to','a','is']);
  const map = new Map();
  rows.forEach((row) => {
    String(row.clean_content || row.Content || '').toLowerCase().split(/\s+/).forEach((word) => {
      const clean = word.replace(/[^a-zA-ZÀ-ÿ0-9]/g, '');
      if (clean.length > 3 && !stopwords.has(clean)) map.set(clean, (map.get(clean) || 0) + 1);
    });
  });
  return Array.from(map.entries()).map(([name, value]) => ({ name, value })).sort((a,b)=>b.value-a.value).slice(0, 15);
}

function dateTrend(rows) {
  const map = new Map();
  rows.forEach((row) => {
    const raw = row.CommentAt_parsed || row.CommentAt || '';
    const date = raw && raw !== 'nan' ? String(raw).slice(0, 10) : 'Tanpa tanggal';
    map.set(date, (map.get(date) || 0) + 1);
  });
  return Array.from(map.entries()).map(([date, count]) => ({ date, count })).sort((a,b)=>String(a.date).localeCompare(String(b.date))).slice(-30);
}

function StatCard({ title, value, icon: Icon, subtitle }) {
  return <div className="card stat-card"><div><p>{title}</p><h2>{value}</h2>{subtitle && <span>{subtitle}</span>}</div><Icon size={32} /></div>;
}

export default function App() {
  const [rows, setRows] = useState([]);
  const [platform, setPlatform] = useState('Semua');
  const [sentiment, setSentiment] = useState('Semua');
  const [keyword, setKeyword] = useState('');
  const [minReaction, setMinReaction] = useState(0);

  useEffect(() => {
    Papa.parse('/data/sumud_comments_sentiment.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (result) => setRows(result.data.map((r, i) => ({ ...r, _row: i + 1 }))),
    });
  }, []);

  const filtered = useMemo(() => rows.filter((row) => {
    const text = `${row.Content || ''} ${row.Author || ''}`.toLowerCase();
    const okPlatform = platform === 'Semua' || row.Platform === platform;
    const okSentiment = sentiment === 'Semua' || row.Sentiment === sentiment;
    const okKeyword = !keyword || text.includes(keyword.toLowerCase());
    const okReaction = normalizeNumber(row.ReactionsCount) >= Number(minReaction || 0);
    return okPlatform && okSentiment && okKeyword && okReaction;
  }), [rows, platform, sentiment, keyword, minReaction]);

  const sentimentData = countBy(filtered, 'Sentiment').sort((a,b)=> ['Positif','Netral','Negatif'].indexOf(a.name) - ['Positif','Netral','Negatif'].indexOf(b.name));
  const platformData = countBy(filtered, 'Platform');
  const authorData = topAuthors(filtered);
  const wordData = topWords(filtered);
  const trendData = dateTrend(filtered);
  const totalReactions = filtered.reduce((sum, row) => sum + normalizeNumber(row.ReactionsCount), 0);
  const uniqueAuthors = new Set(filtered.map((r)=>r.Author).filter(Boolean)).size;

  return <main>
    <section className="hero">
      <div>
        <p className="eyebrow">Dashboard Analitik Media Sosial</p>
        <h1>Analisis Sentimen Percakapan YouTube dan Facebook tentang Sumud Flotilla</h1>
        <p className="lead">Dashboard Vercel ini menggunakan data statis CSV yang telah diproses dari komentar YouTube dan Facebook. Klasifikasi sentimen terdiri atas positif, negatif, dan netral.</p>
      </div>
      <button className="download" onClick={() => downloadCsv(filtered, 'sumud_flotilla_filtered_sentiment.csv')}><Download size={18}/> Export CSV</button>
    </section>

    <section className="filters card">
      <div><Filter size={18}/><strong>Filter Analisis</strong></div>
      <select value={platform} onChange={(e)=>setPlatform(e.target.value)}><option>Semua</option><option>YouTube</option><option>Facebook</option></select>
      <select value={sentiment} onChange={(e)=>setSentiment(e.target.value)}><option>Semua</option><option>Positif</option><option>Netral</option><option>Negatif</option></select>
      <label>Min. Reaksi <input type="number" value={minReaction} min="0" onChange={(e)=>setMinReaction(e.target.value)} /></label>
      <label className="search"><Search size={16}/><input placeholder="Cari kata kunci/author..." value={keyword} onChange={(e)=>setKeyword(e.target.value)} /></label>
    </section>

    <section className="grid stats">
      <StatCard title="Total Komentar" value={filtered.length.toLocaleString('id-ID')} icon={MessageCircle} />
      <StatCard title="Penulis Unik" value={uniqueAuthors.toLocaleString('id-ID')} icon={Users} />
      <StatCard title="Total Reaksi" value={totalReactions.toLocaleString('id-ID')} icon={BarChart3} />
      <StatCard title="Sumber Data" value={platform === 'Semua' ? '2 Platform' : platform} icon={Filter} subtitle="YouTube/Facebook" />
    </section>

    <section className="grid two">
      <div className="card chart-card"><h3>Pie Chart Distribusi Sentimen</h3><ResponsiveContainer width="100%" height={320}><PieChart><Pie data={sentimentData} dataKey="value" nameKey="name" outerRadius={105} label>{sentimentData.map((entry, index) => <Cell key={index} fill={SENTIMENT_COLORS[entry.name] || '#94a3b8'} />)}</Pie><Tooltip/><Legend/></PieChart></ResponsiveContainer></div>
      <div className="card chart-card"><h3>Distribusi Platform</h3><ResponsiveContainer width="100%" height={320}><BarChart data={platformData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value">{platformData.map((entry, index) => <Cell key={index} fill={PLATFORM_COLORS[entry.name] || '#64748b'} />)}</Bar></BarChart></ResponsiveContainer></div>
    </section>

    <section className="grid two">
      <div className="card chart-card"><h3>Tren Komentar Berdasarkan Tanggal</h3><ResponsiveContainer width="100%" height={320}><LineChart data={trendData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="date" angle={-25} textAnchor="end" height={70}/><YAxis/><Tooltip/><Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={3} /></LineChart></ResponsiveContainer></div>
      <div className="card chart-card"><h3>Kata Kunci Dominan</h3><ResponsiveContainer width="100%" height={320}><BarChart data={wordData} layout="vertical"><CartesianGrid strokeDasharray="3 3"/><XAxis type="number"/><YAxis type="category" dataKey="name" width={110}/><Tooltip/><Bar dataKey="value" fill="#7c3aed" /></BarChart></ResponsiveContainer></div>
    </section>

    <section className="card table-card"><h3>Ringkasan Sentimen</h3><table><thead><tr><th>Sentimen</th><th>Jumlah</th><th>Persentase</th></tr></thead><tbody>{sentimentData.map((row)=><tr key={row.name}><td><span className={`pill ${row.name}`}>{row.name}</span></td><td>{row.value}</td><td>{filtered.length ? ((row.value/filtered.length)*100).toFixed(1) : 0}%</td></tr>)}</tbody></table></section>

    <section className="card table-card"><h3>Tabel Hasil Sentimen per Komentar</h3><div className="table-wrap"><table><thead><tr><th>No</th><th>Platform</th><th>Author</th><th>Komentar</th><th>Reaksi</th><th>Sentimen</th><th>Skor</th></tr></thead><tbody>{filtered.slice(0, 250).map((row, idx)=><tr key={`${row._row}-${idx}`}><td>{idx+1}</td><td>{row.Platform}</td><td>{row.Author}</td><td className="comment">{row.Content}</td><td>{row.ReactionsCount || 0}</td><td><span className={`pill ${row.Sentiment}`}>{row.Sentiment}</span></td><td>{row.SentimentScore}</td></tr>)}</tbody></table></div><p className="note">Tabel menampilkan maksimal 250 baris pertama sesuai filter. Gunakan Export CSV untuk seluruh hasil filter.</p></section>
  </main>;
}
