import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card, Button, Tag, Space, message, Select, Row, Col, 
  Statistic, Spin, Typography, Divider, Empty
} from 'antd';
import {
  CheckCircleOutlined, CloseCircleOutlined, LeftOutlined, 
  RightOutlined, SyncOutlined, DownloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

interface ChapterInfo {
  id: string;
  chapter_number: number;
  title: string;
  review_status: string;
}

interface DiffData {
  chapter_id: string;
  chapter_number: number;
  original_word_count: number;
  refined_word_count: number;
  segments: {
    segment: number;
    original: string;
    refined: string;
    original_words: number;
    refined_words: number;
  }[];
  status: string;
}

interface ReviewSummary {
  total: number;
  approved: number;
  rejected: number;
  pending: number;
}

export default function RefinementReview() {
  const { projectId } = useParams<{ projectId: string }>();
  const [chapters, setChapters] = useState<ChapterInfo[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [diffData, setDiffData] = useState<DiffData | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<ReviewSummary>({ total: 0, approved: 0, rejected: 0, pending: 0 });

  // 加载章节列表
  const fetchChapters = useCallback(async () => {
    if (!projectId) return;
    try {
      const [chaptersRes, summaryRes] = await Promise.all([
        fetch(`/api/refinement/project/${projectId}/chapters`),
        fetch(`/api/refinement/project/${projectId}/review-summary`)
      ]);
      const chaptersData = await chaptersRes.json();
      const summaryData = await summaryRes.json();
      
      // 只显示已优化的章节
      const refinedChapters = (chaptersData.chapters || []).filter((c: any) => c.is_refined);
      setChapters(refinedChapters);
      setSummary(summaryData);
    } catch {
      message.error('加载章节列表失败');
    }
  }, [projectId]);

  // 加载当前章节的对比数据
  const fetchDiff = useCallback(async (chapterId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/refinement/chapter/${chapterId}/diff`);
      if (res.ok) {
        const data = await res.json();
        setDiffData(data);
      } else {
        setDiffData(null);
      }
    } catch {
      setDiffData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChapters();
  }, [fetchChapters]);

  useEffect(() => {
    if (chapters.length > 0 && chapters[currentIndex]) {
      fetchDiff(chapters[currentIndex].id);
    }
  }, [chapters, currentIndex, fetchDiff]);

  const currentChapter = chapters[currentIndex];
  const isApproved = currentChapter?.review_status === 'approved';

  // 审核操作
  const handleReview = async (status: 'approved' | 'rejected') => {
    if (!currentChapter) return;
    try {
      await fetch(`/api/refinement/chapter/${currentChapter.id}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      message.success(status === 'approved' ? '✓ 已通过' : '✗ 已标记需修改');
      
      // 更新本地状态
      setChapters(prev => prev.map((c, i) => 
        i === currentIndex ? { ...c, review_status: status } : c
      ));
      setSummary(prev => ({
        ...prev,
        approved: status === 'approved' ? prev.approved + 1 : prev.approved,
        rejected: status === 'rejected' ? prev.rejected + 1 : prev.rejected,
        pending: prev.pending - 1
      }));
      
      // 自动跳转到下一章
      if (currentIndex < chapters.length - 1) {
        setCurrentIndex(currentIndex + 1);
      }
    } catch {
      message.error('审核失败');
    }
  };

  // 导航
  const goPrev = () => currentIndex > 0 && setCurrentIndex(currentIndex - 1);
  const goNext = () => currentIndex < chapters.length - 1 && setCurrentIndex(currentIndex + 1);

  // 合并所有段落的文本
  const getFullText = (type: 'original' | 'refined') => {
    if (!diffData?.segments) return '';
    return diffData.segments.map(s => type === 'original' ? s.original : s.refined).join('\n\n');
  };

  // 导出
  const handleExport = (format: string) => {
    window.open(`/api/refinement/project/${projectId}/export?format=${format}`, '_blank');
  };

  if (chapters.length === 0) {
    return (
      <div style={{ padding: 24 }}>
        <Card>
          <Empty description="暂无已优化的章节" />
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Button onClick={fetchChapters} icon={<SyncOutlined />}>刷新</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: 24, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部统计和导航 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space size="large">
              <Statistic title="总章节" value={summary.total} />
              <Statistic title="已通过" value={summary.approved} valueStyle={{ color: '#52c41a' }} />
              <Statistic title="待审核" value={summary.pending} valueStyle={{ color: '#faad14' }} />
            </Space>
          </Col>
          <Col>
            <Space>
              <Select
                style={{ width: 280 }}
                value={currentIndex}
                onChange={setCurrentIndex}
                options={chapters.map((c, i) => ({
                  value: i,
                  label: (
                    <span>
                      第{c.chapter_number}章 {c.title?.substring(0, 15)}
                      {c.review_status === 'approved' && <Tag color="green" style={{ marginLeft: 8 }}>已通过</Tag>}
                      {c.review_status === 'rejected' && <Tag color="red" style={{ marginLeft: 8 }}>需修改</Tag>}
                    </span>
                  )
                }))}
              />
              <Button icon={<LeftOutlined />} onClick={goPrev} disabled={currentIndex === 0} />
              <Text>{currentIndex + 1} / {chapters.length}</Text>
              <Button icon={<RightOutlined />} onClick={goNext} disabled={currentIndex === chapters.length - 1} />
              <Divider type="vertical" />
              <Button icon={<DownloadOutlined />} onClick={() => handleExport('txt')}>导出TXT</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 主内容区 */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ textAlign: 'center', paddingTop: 100 }}><Spin size="large" /></div>
        ) : !diffData ? (
          <Empty description="无法加载对比数据" />
        ) : isApproved ? (
          /* 已审核通过：只显示优化后的版本 */
          <Card 
            title={
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                <span>第{currentChapter.chapter_number}章 {currentChapter.title}</span>
                <Tag color="green">已通过审核</Tag>
                <Text type="secondary">({diffData.refined_word_count.toLocaleString()} 字)</Text>
              </Space>
            }
            style={{ height: '100%', overflow: 'auto' }}
          >
            <pre style={{ 
              whiteSpace: 'pre-wrap', 
              fontSize: 15, 
              lineHeight: 1.8,
              fontFamily: 'inherit'
            }}>
              {getFullText('refined')}
            </pre>
          </Card>
        ) : (
          /* 待审核：左右对比显示 */
          <>
            <Row gutter={16} style={{ height: 'calc(100% - 60px)' }}>
              {/* 左侧：原文 */}
              <Col span={12} style={{ height: '100%' }}>
                <Card 
                  title={
                    <Space>
                      <span>原文</span>
                      <Text type="secondary">({diffData.original_word_count.toLocaleString()} 字)</Text>
                    </Space>
                  }
                  size="small"
                  style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                  bodyStyle={{ flex: 1, overflow: 'auto', padding: 16 }}
                >
                  <pre style={{ 
                    whiteSpace: 'pre-wrap', 
                    fontSize: 14, 
                    lineHeight: 1.8,
                    fontFamily: 'inherit',
                    margin: 0
                  }}>
                    {getFullText('original')}
                  </pre>
                </Card>
              </Col>
              
              {/* 右侧：优化后 */}
              <Col span={12} style={{ height: '100%' }}>
                <Card 
                  title={
                    <Space>
                      <span>优化后</span>
                      <Text type="secondary">({diffData.refined_word_count.toLocaleString()} 字)</Text>
                      <Tag color={diffData.refined_word_count >= diffData.original_word_count ? 'green' : 'orange'}>
                        {diffData.refined_word_count >= diffData.original_word_count ? '+' : ''}
                        {diffData.refined_word_count - diffData.original_word_count} 字
                      </Tag>
                    </Space>
                  }
                  size="small"
                  style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                  bodyStyle={{ flex: 1, overflow: 'auto', padding: 16 }}
                >
                  <pre style={{ 
                    whiteSpace: 'pre-wrap', 
                    fontSize: 14, 
                    lineHeight: 1.8,
                    fontFamily: 'inherit',
                    margin: 0
                  }}>
                    {getFullText('refined')}
                  </pre>
                </Card>
              </Col>
            </Row>

            {/* 底部审核按钮 */}
            <div style={{ 
              marginTop: 16, 
              textAlign: 'center',
              padding: '12px 0',
              background: '#fafafa',
              borderRadius: 8
            }}>
              <Space size="large">
                <Button 
                  size="large"
                  danger 
                  icon={<CloseCircleOutlined />} 
                  onClick={() => handleReview('rejected')}
                >
                  需要修改
                </Button>
                <Title level={4} style={{ margin: '0 24px' }}>
                  第{currentChapter.chapter_number}章 - {currentChapter.title}
                </Title>
                <Button 
                  size="large"
                  type="primary" 
                  icon={<CheckCircleOutlined />} 
                  onClick={() => handleReview('approved')}
                >
                  通过审核
                </Button>
              </Space>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
