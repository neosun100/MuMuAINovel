import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Empty, Modal, message, Spin, Row, Col, Statistic, Space, Tag, Progress, Typography, Badge, Alert, Upload, Checkbox, Divider, Switch, Dropdown, Form, Input, InputNumber } from 'antd';
import { EditOutlined, DeleteOutlined, BookOutlined, RocketOutlined, CalendarOutlined, FileTextOutlined, TrophyOutlined, FireOutlined, SettingOutlined, InfoCircleOutlined, CloseOutlined, UploadOutlined, DownloadOutlined, ApiOutlined, MoreOutlined, BulbOutlined, LoadingOutlined, FileSearchOutlined, ReadOutlined } from '@ant-design/icons';
import { projectApi, chapterApi } from '../services/api';
import { useStore } from '../store';
import { useProjectSync } from '../store/hooks';
import type { ReactNode } from 'react';
import { cardStyles, cardHoverHandlers, gridConfig } from '../components/CardStyles';
import UserMenu from '../components/UserMenu';
import ChangelogFloatingButton from '../components/ChangelogFloatingButton';

const { Title, Text, Paragraph } = Typography;

export default function ProjectList() {
  const navigate = useNavigate();
  const { projects, loading } = useStore();
  const [modal, contextHolder] = Modal.useModal();
  const [showApiTip, setShowApiTip] = useState(true);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [importing, setImporting] = useState(false);
  const [validating, setValidating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [selectedProjectIds, setSelectedProjectIds] = useState<string[]>([]);
  const [exportOptions, setExportOptions] = useState({
    includeWritingStyles: true,
    includeGenerationHistory: true,
  });
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<any>(null);
  const [editForm] = Form.useForm();
  const [updating, setUpdating] = useState(false);
  const [chapterStats, setChapterStats] = useState<Record<string, { total: number; completed: number; firstChapterId?: string }>>({});

  const { refreshProjects, deleteProject } = useProjectSync();

  useEffect(() => {
    refreshProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 获取每个项目的章节统计
  useEffect(() => {
    const fetchChapterStats = async () => {
      if (!projects || projects.length === 0) return;
      const stats: Record<string, { total: number; completed: number; firstChapterId?: string }> = {};
      await Promise.all(
        projects.map(async (project: any) => {
          try {
            const res = await chapterApi.getChapters(project.id);
            const items = (res as any).items || res || [];
            const completedChapters = items.filter((c: any) => c.word_count > 0).sort((a: any, b: any) => a.chapter_number - b.chapter_number);
            stats[project.id] = {
              total: items.length,
              completed: completedChapters.length,
              firstChapterId: completedChapters[0]?.id
            };
          } catch {
            stats[project.id] = { total: 0, completed: 0 };
          }
        })
      );
      setChapterStats(stats);
    };
    fetchChapterStats();
  }, [projects]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        refreshProjects();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = (id: string) => {
    const isMobile = window.innerWidth <= 768;
    modal.confirm({
      title: '确认删除',
      content: '删除项目将同时删除所有相关数据，此操作不可恢复。确定要删除吗？',
      okText: '确定',
      cancelText: '取消',
      okType: 'danger',
      centered: true,
      ...(isMobile && {
        style: { top: 'auto' }
      }),
      onOk: async () => {
        try {
          await deleteProject(id);
          message.success('项目删除成功');
        } catch {
          message.error('删除项目失败');
        }
      },
    });
  };

  const handleEditProject = (project: any) => {
    setEditingProject(project);
    editForm.setFieldsValue({
      description: project.description || '',
      target_words: project.target_words || 0,
    });
    setEditModalVisible(true);
  };

  const handleCloseEditModal = () => {
    setEditModalVisible(false);
    setEditingProject(null);
    editForm.resetFields();
  };

  const handleUpdateProject = async () => {
    try {
      const values = await editForm.validateFields();
      setUpdating(true);

      await projectApi.updateProject(editingProject.id, {
        description: values.description,
        target_words: values.target_words,
      });

      message.success('项目更新成功');
      handleCloseEditModal();
      await refreshProjects();
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请检查表单填写');
      } else {
        message.error('更新失败，请重试');
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleEnterProject = async (project: any) => {
    // 检查项目是否未完成生成(wizard_status为incomplete)
    if (project.wizard_status === 'incomplete') {
      // 未完成的项目跳转到生成页面继续生成
      navigate(`/wizard?project_id=${project.id}`);
    } else {
      // 已完成的项目进入项目详情页
      navigate(`/project/${project.id}`);
    }
  };

  const getStatusTag = (status: string) => {
    const statusConfig: Record<string, { color: string; text: string; icon: ReactNode }> = {
      planning: { color: 'blue', text: '规划中', icon: <CalendarOutlined /> },
      writing: { color: 'green', text: '创作中', icon: <EditOutlined /> },
      revising: { color: 'orange', text: '修改中', icon: <FileTextOutlined /> },
      completed: { color: 'purple', text: '已完成', icon: <TrophyOutlined /> },
    };
    const config = statusConfig[status] || statusConfig.planning;
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  const getProgress = (current: number, target: number) => {
    if (!target) return 0;
    return Math.min(Math.round((current / target) * 100), 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return '#52c41a';
    if (progress >= 50) return '#1890ff';
    if (progress >= 20) return '#faad14';
    return '#ff4d4f';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return '今天';
    if (days === 1) return '昨天';
    if (days < 7) return `${days}天前`;
    if (days < 30) return `${Math.floor(days / 7)}周前`;
    return date.toLocaleDateString('zh-CN');
  };

  const totalWords = projects.reduce((sum, p) => sum + (p.current_words || 0), 0);
  const activeProjects = projects.filter(p => p.status === 'writing').length;

  // 处理文件选择
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setValidationResult(null);

    // 验证文件
    try {
      setValidating(true);
      const result = await projectApi.validateImportFile(file);
      setValidationResult(result);

      if (!result.valid) {
        message.error('文件验证失败');
      }
    } catch (error) {
      console.error('验证失败:', error);
      message.error('文件验证失败');
    } finally {
      setValidating(false);
    }

    return false; // 阻止自动上传
  };

  // 处理导入
  const handleImport = async () => {
    if (!selectedFile || !validationResult?.valid) {
      message.warning('请选择有效的导入文件');
      return;
    }

    try {
      setImporting(true);
      const result = await projectApi.importProject(selectedFile);

      if (result.success) {
        message.success(`项目导入成功！${result.message}`);
        setImportModalVisible(false);
        setSelectedFile(null);
        setValidationResult(null);

        // 刷新项目列表
        await refreshProjects();

        // 跳转到新项目
        if (result.project_id) {
          navigate(`/project/${result.project_id}`);
        }
      } else {
        message.error(result.message || '导入失败');
      }
    } catch (error) {
      console.error('导入失败:', error);
      message.error('导入失败，请重试');
    } finally {
      setImporting(false);
    }
  };

  // 关闭导入对话框
  const handleCloseImportModal = () => {
    setImportModalVisible(false);
    setSelectedFile(null);
    setValidationResult(null);
  };

  // 打开导出对话框
  const handleOpenExportModal = () => {
    setExportModalVisible(true);
    setSelectedProjectIds([]);
  };

  // 获取所有可导出的项目
  const exportableProjects = projects;

  // 关闭导出对话框
  const handleCloseExportModal = () => {
    setExportModalVisible(false);
    setSelectedProjectIds([]);
  };

  // 切换项目选择
  const handleToggleProject = (projectId: string) => {
    setSelectedProjectIds(prev =>
      prev.includes(projectId)
        ? prev.filter(id => id !== projectId)
        : [...prev, projectId]
    );
  };

  // 全选/取消全选
  const handleToggleAll = () => {
    if (selectedProjectIds.length === exportableProjects.length) {
      setSelectedProjectIds([]);
    } else {
      setSelectedProjectIds(exportableProjects.map(p => p.id));
    }
  };

  // 执行导出
  const handleExport = async () => {
    if (selectedProjectIds.length === 0) {
      message.warning('请至少选择一个项目');
      return;
    }

    try {
      setExporting(true);

      if (selectedProjectIds.length === 1) {
        // 单个项目导出
        const projectId = selectedProjectIds[0];
        const project = projects.find(p => p.id === projectId);
        await projectApi.exportProjectData(projectId, {
          include_generation_history: exportOptions.includeGenerationHistory,
          include_writing_styles: exportOptions.includeWritingStyles
        });
        message.success(`项目 "${project?.title}" 导出成功`);
      } else {
        // 批量导出
        let successCount = 0;
        let failCount = 0;

        for (const projectId of selectedProjectIds) {
          try {
            await projectApi.exportProjectData(projectId, {
              include_generation_history: exportOptions.includeGenerationHistory,
              include_writing_styles: exportOptions.includeWritingStyles
            });
            successCount++;
            // 添加延迟避免浏览器阻止多个下载
            await new Promise(resolve => setTimeout(resolve, 500));
          } catch (error) {
            console.error(`导出项目 ${projectId} 失败:`, error);
            failCount++;
          }
        }

        if (failCount === 0) {
          message.success(`成功导出 ${successCount} 个项目`);
        } else {
          message.warning(`导出完成：成功 ${successCount} 个，失败 ${failCount} 个`);
        }
      }

      handleCloseExportModal();
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请重试');
    } finally {
      setExporting(false);
    }
  };

  // 计算页脚高度和页面内边距
  const isMobile = window.innerWidth <= 768;
  const footerHeight = isMobile ? 48 : 52;
  const topPadding = isMobile ? 20 : 32;
  const sidePadding = isMobile ? 16 : 24;

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(180deg, var(--color-bg-base) 0%, #EEF2F3 100%)',
      overflow: 'hidden'
    }}>
      {contextHolder}

      {/* 固定头部区域 */}
      <div style={{
        flexShrink: 0,
        padding: `${topPadding}px ${sidePadding}px 0`,
      }}>
        <div style={{
          maxWidth: 1800,
          margin: '0 auto'
        }}>
          {/* 现代化头部区域 */}
          <Card
            variant="borderless"
            style={{
              background: 'linear-gradient(135deg, var(--color-primary) 0%, #5A9BA5 50%, var(--color-primary-hover) 100%)',
              borderRadius: window.innerWidth <= 768 ? 16 : 24,
              boxShadow: '0 12px 40px rgba(77, 128, 136, 0.25), 0 4px 12px rgba(0, 0, 0, 0.06)',
              border: 'none',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {/* 装饰性背景元素 */}
            <div style={{
              position: 'absolute',
              top: -60,
              right: -60,
              width: 200,
              height: 200,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.08)',
              pointerEvents: 'none'
            }} />
            <div style={{
              position: 'absolute',
              bottom: -40,
              left: '30%',
              width: 120,
              height: 120,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.05)',
              pointerEvents: 'none'
            }} />
            <div style={{
              position: 'absolute',
              top: '50%',
              right: '15%',
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.06)',
              pointerEvents: 'none'
            }} />
            <Row align="middle" justify="space-between" gutter={[16, 16]} style={{ position: 'relative', zIndex: 1 }}>
              <Col xs={24} sm={12} md={10}>
                <Space direction="vertical" size={8}>
                  <Title level={window.innerWidth <= 768 ? 3 : 2} style={{ margin: 0, color: '#fff', textShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                    <FireOutlined style={{ color: 'rgba(255,255,255,0.9)', marginRight: 12 }} />
                    我的创作空间
                  </Title>
                  <Text style={{ fontSize: window.innerWidth <= 768 ? 13 : 15, color: 'rgba(255,255,255,0.85)' }}>
                    ✨ 开启你的小说创作之旅
                  </Text>
                </Space>
              </Col>
              <Col xs={24} sm={12} md={14}>
                {window.innerWidth <= 768 ? (
                  // 移动端：优化布局
                  <Space direction="vertical" size={8} style={{ width: '100%' }}>
                    {/* 第一行：主要创建按钮 */}
                    <Row gutter={8}>
                      <Col span={12}>
                        <Button
                          type="primary"
                          size="middle"
                          icon={<BulbOutlined />}
                          onClick={() => navigate('/inspiration')}
                          block
                          style={{
                            borderRadius: 10,
                            background: 'rgba(255, 193, 7, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            boxShadow: '0 4px 12px rgba(255, 193, 7, 0.35)',
                            color: '#fff',
                            height: 42,
                            fontWeight: 500
                          }}
                        >
                          灵感模式
                        </Button>
                      </Col>
                      <Col span={12}>
                        <Button
                          type="primary"
                          size="middle"
                          icon={<RocketOutlined />}
                          onClick={() => navigate('/wizard')}
                          block
                          style={{
                            borderRadius: 10,
                            background: 'rgba(255, 255, 255, 0.2)',
                            border: '1px solid rgba(255, 255, 255, 0.4)',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                            color: '#fff',
                            height: 42,
                            fontWeight: 500,
                            backdropFilter: 'blur(8px)'
                          }}
                        >
                          向导创建
                        </Button>
                      </Col>
                    </Row>
                    {/* 第二行：功能按钮 */}
                    <Row gutter={8}>
                      <Col span={8}>
                        <Button
                          type="default"
                          size="middle"
                          icon={<SettingOutlined />}
                          onClick={() => navigate('/settings')}
                          block
                          style={{
                            borderRadius: 10,
                            background: 'rgba(255, 255, 255, 0.15)',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                            height: 38,
                            padding: '0 8px',
                            color: '#fff',
                            backdropFilter: 'blur(8px)'
                          }}
                        >
                          设置
                        </Button>
                      </Col>
                      <Col span={8}>
                        <Dropdown
                          menu={{
                            items: [
                              {
                                key: 'export',
                                label: '导出项目',
                                icon: <DownloadOutlined />,
                                onClick: handleOpenExportModal,
                                disabled: exportableProjects.length === 0
                              },
                              {
                                key: 'import',
                                label: '导入项目',
                                icon: <UploadOutlined />,
                                onClick: () => setImportModalVisible(true)
                              },
                              {
                                type: 'divider'
                              },
                              {
                                key: 'prompt-templates',
                                label: '提示词管理',
                                icon: <FileSearchOutlined />,
                                onClick: () => navigate('/prompt-templates')
                              },
                              {
                                key: 'mcp',
                                label: 'MCP插件',
                                icon: <ApiOutlined />,
                                onClick: () => navigate('/mcp-plugins')
                              }
                            ]
                          }}
                          placement="bottomRight"
                          trigger={['click']}
                        >
                          <Button
                            size="middle"
                            icon={<MoreOutlined />}
                            block
                            style={{
                              borderRadius: 10,
                              background: 'rgba(255, 255, 255, 0.15)',
                              border: '1px solid rgba(255, 255, 255, 0.3)',
                              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                              height: 38,
                              color: '#fff',
                              backdropFilter: 'blur(8px)'
                            }}
                          >
                            更多
                          </Button>
                        </Dropdown>
                      </Col>
                      <Col span={8}>
                        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <UserMenu />
                        </div>
                      </Col>
                    </Row>
                  </Space>
                ) : (
                  // PC端：优化后的布局 - 主要按钮 + 下拉菜单
                  <Space size={12} style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      type="primary"
                      size="large"
                      icon={<BulbOutlined />}
                      onClick={() => navigate('/inspiration')}
                      style={{
                        borderRadius: 12,
                        background: 'rgba(255, 193, 7, 0.95)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 4px 16px rgba(255, 193, 7, 0.4)',
                        color: '#fff',
                        fontWeight: 600,
                        height: 44,
                        transition: 'all 0.3s ease'
                      }}
                    >
                      灵感模式
                    </Button>
                    <Button
                      type="primary"
                      size="large"
                      icon={<RocketOutlined />}
                      onClick={() => navigate('/wizard')}
                      style={{
                        borderRadius: 12,
                        background: 'rgba(255, 255, 255, 0.2)',
                        border: '1px solid rgba(255, 255, 255, 0.4)',
                        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
                        color: '#fff',
                        fontWeight: 500,
                        height: 44,
                        backdropFilter: 'blur(10px)',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      向导创建
                    </Button>
                    <Button
                      type="default"
                      size="large"
                      icon={<SettingOutlined />}
                      onClick={() => navigate('/settings')}
                      style={{
                        borderRadius: 12,
                        background: 'rgba(255, 255, 255, 0.15)',
                        border: '1px solid rgba(255, 255, 255, 0.3)',
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                        color: '#fff',
                        height: 44,
                        backdropFilter: 'blur(10px)',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      API设置
                    </Button>
                    <Dropdown
                      menu={{
                        items: [
                          {
                            key: 'export',
                            label: '导出项目',
                            icon: <DownloadOutlined />,
                            onClick: handleOpenExportModal,
                            disabled: exportableProjects.length === 0
                          },
                          {
                            key: 'import',
                            label: '导入项目',
                            icon: <UploadOutlined />,
                            onClick: () => setImportModalVisible(true)
                          },
                          {
                            type: 'divider'
                          },
                          {
                            key: 'prompt-templates',
                            label: '提示词管理',
                            icon: <FileSearchOutlined />,
                            onClick: () => navigate('/prompt-templates')
                          },
                          {
                            key: 'mcp',
                            label: 'MCP插件',
                            icon: <ApiOutlined />,
                            onClick: () => navigate('/mcp-plugins')
                          }
                        ]
                      }}
                      placement="bottomRight"
                    >
                      <Button
                        size="large"
                        icon={<MoreOutlined />}
                        style={{
                          borderRadius: 12,
                          background: 'rgba(255, 255, 255, 0.15)',
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                          color: '#fff',
                          height: 44,
                          backdropFilter: 'blur(10px)',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        更多
                      </Button>
                    </Dropdown>
                    <UserMenu />
                  </Space>
                )}
              </Col>
            </Row>

            {showApiTip && projects.length === 0 && (
              <Alert
                message={
                  <Space align="center" style={{ width: '100%' }}>
                    <InfoCircleOutlined style={{ fontSize: 16, color: '#1890ff' }} />
                    <Text strong style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>
                      首次使用提示
                    </Text>
                  </Space>
                }
                description={
                  <Space direction="vertical" size={8} style={{ width: '100%' }}>
                    <Text style={{ fontSize: window.innerWidth <= 768 ? 12 : 13 }}>
                      在开始创作之前，请先配置您的AI接口。系统支持OpenAI和Anthropic两种接口。
                    </Text>
                    <Space size={8}>
                      <Button
                        type="primary"
                        size="small"
                        icon={<SettingOutlined />}
                        onClick={() => navigate('/settings')}
                        style={{
                          borderRadius: 6,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          border: 'none'
                        }}
                      >
                        立即配置
                      </Button>
                      <Button
                        size="small"
                        onClick={() => setShowApiTip(false)}
                        style={{ borderRadius: 6 }}
                      >
                        暂不提醒
                      </Button>
                    </Space>
                  </Space>
                }
                type="info"
                showIcon={false}
                closable
                closeIcon={<CloseOutlined style={{ fontSize: 12 }} />}
                onClose={() => setShowApiTip(false)}
                style={{
                  marginTop: window.innerWidth <= 768 ? 16 : 24,
                  borderRadius: 12,
                  background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%)',
                  border: '1px solid #91d5ff'
                }}
              />
            )}

            {projects.length > 0 && (
              <Row gutter={[isMobile ? 8 : 16, 16]} style={{ marginTop: isMobile ? 16 : 28, position: 'relative', zIndex: 1 }}>
                <Col xs={8} sm={8}>
                  <Card
                    variant="borderless"
                    style={{
                      background: 'rgba(255, 255, 255, 0.2)',
                      borderRadius: isMobile ? 12 : 16,
                      border: '1px solid rgba(255, 255, 255, 0.3)',
                      backdropFilter: 'blur(10px)',
                      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
                      padding: isMobile ? '8px 4px' : '12px'
                    }}
                    styles={{ body: { padding: isMobile ? '4px' : '12px' } }}
                  >
                    <Statistic
                      title={
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: isMobile ? 4 : 8 }}>
                          <span style={{ fontSize: isMobile ? 16 : 24, color: 'rgba(255,255,255,0.9)', marginRight: isMobile ? 0 : 8 }}>📚</span>
                          {!isMobile && <span style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>总项目数</span>}
                          {isMobile && <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>项目</div>}
                        </div>
                      }
                      value={projects.length}
                      valueStyle={{
                        color: '#fff',
                        fontSize: isMobile ? 18 : 32,
                        fontWeight: 'bold',
                        textShadow: '0 1px 2px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                      }}
                    />
                  </Card>
                </Col>
                <Col xs={8} sm={8}>
                  <Card
                    variant="borderless"
                    style={{
                      background: 'rgba(255, 255, 255, 0.2)',
                      borderRadius: isMobile ? 12 : 16,
                      border: '1px solid rgba(255, 255, 255, 0.3)',
                      backdropFilter: 'blur(10px)',
                      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
                      padding: isMobile ? '8px 4px' : '12px'
                    }}
                    styles={{ body: { padding: isMobile ? '4px' : '12px' } }}
                  >
                    <Statistic
                      title={
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: isMobile ? 4 : 8 }}>
                          <span style={{ fontSize: isMobile ? 16 : 24, color: 'rgba(255,255,255,0.9)', marginRight: isMobile ? 0 : 8 }}>✍️</span>
                          {!isMobile && <span style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>创作中</span>}
                          {isMobile && <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>创作</div>}
                        </div>
                      }
                      value={activeProjects}
                      valueStyle={{
                        color: '#fff',
                        fontSize: isMobile ? 18 : 32,
                        fontWeight: 'bold',
                        textShadow: '0 1px 2px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                      }}
                    />
                  </Card>
                </Col>
                <Col xs={8} sm={8}>
                  <Card
                    variant="borderless"
                    style={{
                      background: 'rgba(255, 255, 255, 0.2)',
                      borderRadius: isMobile ? 12 : 16,
                      border: '1px solid rgba(255, 255, 255, 0.3)',
                      backdropFilter: 'blur(10px)',
                      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
                      padding: isMobile ? '8px 4px' : '12px'
                    }}
                    styles={{ body: { padding: isMobile ? '4px' : '12px' } }}
                  >
                    <Statistic
                      title={
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: isMobile ? 4 : 8 }}>
                          <span style={{ fontSize: isMobile ? 16 : 24, color: 'rgba(255,255,255,0.9)', marginRight: isMobile ? 0 : 8 }}>📝</span>
                          {!isMobile && <span style={{ color: 'rgba(255,255,255,0.8)', fontSize: 16 }}>总字数</span>}
                          {isMobile && <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>字数</div>}
                        </div>
                      }
                      value={totalWords}
                      formatter={(value) => {
                        const val = Number(value);
                        return isMobile && val > 10000 ? `${(val / 10000).toFixed(1)}w` : val;
                      }}
                      valueStyle={{
                        color: '#fff',
                        fontSize: isMobile ? 18 : 32,
                        fontWeight: 'bold',
                        textShadow: '0 1px 2px rgba(0,0,0,0.1)',
                        textAlign: 'center'
                      }}
                    />
                  </Card>
                </Col>
              </Row>
            )}
          </Card>
        </div>
      </div>

      {/* 可滚动的项目列表区域 */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        padding: `${isMobile ? 16 : 24}px ${sidePadding}px`,
        paddingBottom: footerHeight + (isMobile ? 24 : 32),
      }}>
        <div style={{ maxWidth: 1800, margin: '0 auto' }}>
          <Spin spinning={loading}>
            {!Array.isArray(projects) || projects.length === 0 ? (
              <Card
                variant="borderless"
                style={{
                  background: 'var(--color-bg-container)',
                  borderRadius: 16,
                  boxShadow: 'var(--shadow-card)',
                  border: '1px solid var(--color-border-secondary)'
                }}
              >
                <Empty
                  description={
                    <Space direction="vertical" size={16}>
                      <Text style={{ fontSize: 16, color: '#8c8c8c' }}>
                        还没有项目，开始创建你的第一个小说项目吧！
                      </Text>
                      <Space size={12}>
                        <Button
                          type="primary"
                          size="large"
                          icon={<BulbOutlined />}
                          onClick={() => navigate('/inspiration')}
                          style={{
                            background: 'var(--color-warning)',
                            border: 'none',
                            color: '#fff',
                            boxShadow: '0 2px 8px rgba(227, 173, 54, 0.2)'
                          }}
                        >
                          灵感模式
                        </Button>
                        <Button
                          type="primary"
                          size="large"
                          icon={<RocketOutlined />}
                          onClick={() => navigate('/wizard')}
                          style={{
                            background: 'var(--color-primary)',
                            border: 'none',
                            boxShadow: '0 2px 8px rgba(77, 128, 136, 0.2)'
                          }}
                        >
                          向导创建
                        </Button>
                      </Space>
                    </Space>
                  }
                  style={{ padding: '80px 0' }}
                />
              </Card>
            ) : (
              <Row gutter={[16, 16]}>
                {projects.map((project) => {
                  const progress = getProgress(project.current_words, project.target_words || 0);

                  return (
                    <Col {...gridConfig} key={project.id}>
                      <Badge.Ribbon
                        text={project.wizard_status === 'incomplete' ? (
                          <Tag color="orange" icon={<LoadingOutlined spin />}>生成中断</Tag>
                        ) : getStatusTag(project.status)}
                        color="transparent"
                        style={{ top: 12, right: 12 }}
                      >
                        <Card
                          hoverable
                          variant="borderless"
                          onClick={() => handleEnterProject(project)}
                          style={cardStyles.project}
                          styles={{ body: { padding: 0, overflow: 'hidden' } }}
                          {...cardHoverHandlers}
                        >
                          {/* 项目卡片头部 - 添加装饰元素 */}
                          <div style={{
                            background: 'linear-gradient(135deg, var(--color-primary) 0%, #5A9BA5 60%, var(--color-primary-hover) 100%)',
                            padding: window.innerWidth <= 768 ? '18px 16px' : '24px',
                            position: 'relative',
                            overflow: 'hidden'
                          }}>
                            {/* 装饰性圆圈 */}
                            <div style={{
                              position: 'absolute',
                              top: -20,
                              right: -20,
                              width: 80,
                              height: 80,
                              borderRadius: '50%',
                              background: 'rgba(255, 255, 255, 0.1)',
                              pointerEvents: 'none'
                            }} />
                            <Space direction="vertical" size={8} style={{ width: '100%', position: 'relative', zIndex: 1 }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: window.innerWidth <= 768 ? 10 : 12 }}>
                                <div style={{
                                  width: window.innerWidth <= 768 ? 36 : 44,
                                  height: window.innerWidth <= 768 ? 36 : 44,
                                  borderRadius: 12,
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  backdropFilter: 'blur(4px)'
                                }}>
                                  <BookOutlined style={{ fontSize: window.innerWidth <= 768 ? 18 : 22, color: '#fff' }} />
                                </div>
                                <Title level={window.innerWidth <= 768 ? 5 : 4} style={{ margin: 0, color: '#fff', flex: 1, textShadow: '0 1px 2px rgba(0,0,0,0.1)' }} ellipsis>
                                  {project.title}
                                </Title>
                              </div>
                              {project.genre && (
                                <Tag
                                  color="rgba(255,255,255,0.2)"
                                  style={{
                                    color: '#fff',
                                    border: '1px solid rgba(255,255,255,0.3)',
                                    borderRadius: 6,
                                    backdropFilter: 'blur(4px)'
                                  }}
                                >
                                  {project.genre}
                                </Tag>
                              )}
                            </Space>
                          </div>

                          <div style={{ padding: window.innerWidth <= 768 ? '16px' : '20px' }}>
                            <Paragraph
                              ellipsis={{ rows: 2 }}
                              style={{
                                color: 'rgba(0,0,0,0.65)',
                                minHeight: 44,
                                marginBottom: 16
                              }}
                            >
                              {project.description || '暂无描述'}
                            </Paragraph>

                            {project.target_words && project.target_words > 0 && (
                              <div style={{ marginBottom: 16 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                  <Text type="secondary" style={{ fontSize: 12 }}>完成进度</Text>
                                  <Text strong style={{ fontSize: 12 }}>{progress}%</Text>
                                </div>
                                <Progress
                                  percent={progress}
                                  strokeColor={getProgressColor(progress)}
                                  showInfo={false}
                                  size={{ height: 8 }}
                                />
                              </div>
                            )}

                            <Row gutter={12}>
                              <Col span={12}>
                                <div style={{
                                  textAlign: 'center',
                                  padding: '14px 0',
                                  background: 'linear-gradient(135deg, #E8F4FC 0%, #F0F9FF 100%)',
                                  borderRadius: 12,
                                  border: '1px solid rgba(24, 144, 255, 0.15)'
                                }}>
                                  <div style={{ fontSize: 22, fontWeight: 'bold', color: 'var(--color-primary)' }}>
                                    {project.current_words >= 1000000
                                      ? (project.current_words / 1000000).toFixed(1) + 'M'
                                      : project.current_words >= 1000
                                        ? (project.current_words / 1000).toFixed(1) + 'K'
                                        : project.current_words
                                    }
                                  </div>
                                  <Text type="secondary" style={{ fontSize: 12 }}>已写字数</Text>
                                </div>
                              </Col>
                              <Col span={12}>
                                <div style={{
                                  textAlign: 'center',
                                  padding: '14px 0',
                                  background: 'linear-gradient(135deg, #FFF7E6 0%, #FFFBE6 100%)',
                                  borderRadius: 12,
                                  border: '1px solid rgba(250, 173, 20, 0.15)'
                                }}>
                                  <div style={{ fontSize: 22, fontWeight: 'bold', color: '#fa8c16' }}>
                                    {chapterStats[project.id] 
                                      ? `${chapterStats[project.id].completed}/${chapterStats[project.id].total}`
                                      : '--'
                                    }
                                  </div>
                                  <Text type="secondary" style={{ fontSize: 12 }}>章节进度</Text>
                                </div>
                              </Col>
                            </Row>

                            {/* 阅读按钮 */}
                            {chapterStats[project.id]?.completed > 0 && chapterStats[project.id]?.firstChapterId && (
                              <Button
                                type="primary"
                                icon={<ReadOutlined />}
                                block
                                style={{ marginTop: 12, borderRadius: 8 }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/chapters/${chapterStats[project.id].firstChapterId}/reader`);
                                }}
                              >
                                阅读文章 ({chapterStats[project.id].completed} 章)
                              </Button>
                            )}

                            <div style={{
                              marginTop: 18,
                              paddingTop: 16,
                              borderTop: '1px solid rgba(0, 0, 0, 0.06)',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center'
                            }}>
                              <Text type="secondary" style={{ fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
                                <CalendarOutlined style={{ color: 'var(--color-primary)' }} />
                                {formatDate(project.updated_at)}
                              </Text>
                              <Space size={4}>
                                <Button
                                  type="text"
                                  size="small"
                                  icon={<EditOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleEditProject(project);
                                  }}
                                  style={{
                                    borderRadius: 8,
                                    color: 'var(--color-primary)',
                                    transition: 'all 0.2s ease'
                                  }}
                                />
                                <Button
                                  type="text"
                                  size="small"
                                  danger
                                  icon={<DeleteOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(project.id);
                                  }}
                                  style={{
                                    borderRadius: 8,
                                    transition: 'all 0.2s ease'
                                  }}
                                />
                              </Space>
                            </div>
                          </div>
                        </Card>
                      </Badge.Ribbon>
                    </Col>
                  );
                })}
              </Row>
            )}
          </Spin>
        </div>

        {/* 导入项目对话框 */}
        <Modal
          title="导入项目"
          open={importModalVisible}
          onOk={handleImport}
          onCancel={handleCloseImportModal}
          confirmLoading={importing}
          okText="导入"
          cancelText="取消"
          width={window.innerWidth <= 768 ? '90%' : 500}
          centered
          okButtonProps={{ disabled: !validationResult?.valid }}
          styles={{
            body: {
              maxHeight: window.innerWidth <= 768 ? '60vh' : 'auto',
              overflowY: 'auto',
              padding: window.innerWidth <= 768 ? '16px' : '24px'
            }
          }}
        >
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <div>
              <p style={{ marginBottom: '12px', color: '#666', fontSize: window.innerWidth <= 768 ? 13 : 14 }}>
                选择之前导出的 JSON 格式项目文件
              </p>
              <Upload
                accept=".json"
                beforeUpload={handleFileSelect}
                maxCount={1}
                onRemove={() => {
                  setSelectedFile(null);
                  setValidationResult(null);
                }}
                fileList={selectedFile ? [{ uid: '-1', name: selectedFile.name, status: 'done' }] as any : []}
              >
                <Button icon={<UploadOutlined />} block>选择文件</Button>
              </Upload>
            </div>

            {validating && (
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <Spin tip="验证文件中..." />
              </div>
            )}

            {validationResult && (
              <Card size="small" style={{ background: validationResult.valid ? '#f6ffed' : '#fff2f0' }}>
                <Space direction="vertical" size={8} style={{ width: '100%' }}>
                  <div>
                    <Text strong style={{
                      color: validationResult.valid ? '#52c41a' : '#ff4d4f',
                      fontSize: window.innerWidth <= 768 ? 13 : 14
                    }}>
                      {validationResult.valid ? '✓ 文件验证通过' : '✗ 文件验证失败'}
                    </Text>
                  </div>

                  {validationResult.project_name && (
                    <div>
                      <Text type="secondary" style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>项目名称：</Text>
                      <Text strong style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>{validationResult.project_name}</Text>
                    </div>
                  )}

                  {validationResult.statistics && Object.keys(validationResult.statistics).length > 0 && (
                    <div>
                      <Text type="secondary" style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>数据统计：</Text>
                      <div style={{ marginTop: 8 }}>
                        <Row gutter={[8, 8]}>
                          {validationResult.statistics.chapters > 0 && (
                            <Col span={12}>
                              <Tag color="blue">章节: {validationResult.statistics.chapters}</Tag>
                            </Col>
                          )}
                          {validationResult.statistics.characters > 0 && (
                            <Col span={12}>
                              <Tag color="green">角色: {validationResult.statistics.characters}</Tag>
                            </Col>
                          )}
                          {validationResult.statistics.outlines > 0 && (
                            <Col span={12}>
                              <Tag color="purple">大纲: {validationResult.statistics.outlines}</Tag>
                            </Col>
                          )}
                          {validationResult.statistics.relationships > 0 && (
                            <Col span={12}>
                              <Tag color="orange">关系: {validationResult.statistics.relationships}</Tag>
                            </Col>
                          )}
                        </Row>
                      </div>
                    </div>
                  )}

                  {validationResult.errors && validationResult.errors.length > 0 && (
                    <div>
                      <Text type="danger" strong style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>错误：</Text>
                      <ul style={{
                        margin: '4px 0 0 0',
                        paddingLeft: '20px',
                        color: '#ff4d4f',
                        fontSize: window.innerWidth <= 768 ? 12 : 13
                      }}>
                        {validationResult.errors.map((error: string, index: number) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {validationResult.warnings && validationResult.warnings.length > 0 && (
                    <div>
                      <Text type="warning" strong style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>警告：</Text>
                      <ul style={{
                        margin: '4px 0 0 0',
                        paddingLeft: '20px',
                        color: '#faad14',
                        fontSize: window.innerWidth <= 768 ? 12 : 13
                      }}>
                        {validationResult.warnings.map((warning: string, index: number) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </Space>
              </Card>
            )}
          </Space>
        </Modal>

        {/* 导出项目对话框 */}
        <Modal
          title="导出项目"
          open={exportModalVisible}
          onOk={handleExport}
          onCancel={handleCloseExportModal}
          confirmLoading={exporting}
          okText={selectedProjectIds.length > 0 ? `导出 (${selectedProjectIds.length})` : '导出'}
          cancelText="取消"
          width={window.innerWidth <= 768 ? '90%' : 700}
          centered
          okButtonProps={{ disabled: selectedProjectIds.length === 0 }}
          styles={{
            body: {
              maxHeight: window.innerWidth <= 768 ? '70vh' : 'auto',
              overflowY: 'auto',
              padding: window.innerWidth <= 768 ? '16px' : '24px'
            }
          }}
        >
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            {/* 导出选项 */}
            <Card
              size="small"
              style={{ background: '#f5f5f5' }}
              styles={{ body: { padding: window.innerWidth <= 768 ? 12 : 16 } }}
            >
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text strong style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>导出选项</Text>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Switch
                    size={window.innerWidth <= 768 ? 'small' : 'default'}
                    checked={exportOptions.includeWritingStyles}
                    onChange={(checked) => setExportOptions(prev => ({ ...prev, includeWritingStyles: checked }))}
                    style={{
                      flexShrink: 0,
                      height: window.innerWidth <= 768 ? 16 : 22,
                      minHeight: window.innerWidth <= 768 ? 16 : 22,
                      lineHeight: window.innerWidth <= 768 ? '16px' : '22px'
                    }}
                  />
                  <Text style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>包含写作风格</Text>
                  <InfoCircleOutlined
                    title="导出项目关联的写作风格数据"
                    style={{ color: '#999', fontSize: window.innerWidth <= 768 ? 12 : 14 }}
                  />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Switch
                    size={window.innerWidth <= 768 ? 'small' : 'default'}
                    checked={exportOptions.includeGenerationHistory}
                    onChange={(checked) => setExportOptions(prev => ({ ...prev, includeGenerationHistory: checked }))}
                    style={{
                      flexShrink: 0,
                      height: window.innerWidth <= 768 ? 16 : 22,
                      minHeight: window.innerWidth <= 768 ? 16 : 22,
                      lineHeight: window.innerWidth <= 768 ? '16px' : '22px'
                    }}
                  />
                  <Text style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>包含生成历史</Text>
                  <InfoCircleOutlined
                    title="导出AI生成的历史记录（最多100条）"
                    style={{ color: '#999', fontSize: window.innerWidth <= 768 ? 12 : 14 }}
                  />
                </div>
              </Space>
            </Card>

            <Divider style={{ margin: '8px 0' }} />

            {/* 项目列表 */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: window.innerWidth <= 768 ? 'wrap' : 'nowrap', gap: 8 }}>
                <Text strong style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>
                  选择要导出的项目 {exportableProjects.length > 0 && <Text type="secondary" style={{ fontSize: window.innerWidth <= 768 ? 12 : 14 }}>({exportableProjects.length}个可导出)</Text>}
                </Text>
                <Checkbox
                  checked={selectedProjectIds.length === exportableProjects.length && exportableProjects.length > 0}
                  indeterminate={selectedProjectIds.length > 0 && selectedProjectIds.length < exportableProjects.length}
                  onChange={handleToggleAll}
                  style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}
                >
                  全选
                </Checkbox>
              </div>

              <div style={{ maxHeight: window.innerWidth <= 768 ? 300 : 400, overflowY: 'auto' }}>
                {exportableProjects.length === 0 ? (
                  <Empty
                    description="暂无可导出的项目"
                    style={{ padding: '40px 0' }}
                  />
                ) : (
                  <Space direction="vertical" size={8} style={{ width: '100%' }}>
                    {exportableProjects.map((project) => (
                      <Card
                        key={project.id}
                        size="small"
                        hoverable
                        style={{
                          cursor: 'pointer',
                          border: selectedProjectIds.includes(project.id) ? '2px solid #1890ff' : '1px solid #d9d9d9',
                          background: selectedProjectIds.includes(project.id) ? '#e6f7ff' : '#fff'
                        }}
                        onClick={() => handleToggleProject(project.id)}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <Checkbox
                            checked={selectedProjectIds.includes(project.id)}
                            onChange={() => handleToggleProject(project.id)}
                            onClick={(e) => e.stopPropagation()}
                          />
                          <BookOutlined style={{ fontSize: 20, color: '#1890ff' }} />
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                              <Text strong style={{ fontSize: window.innerWidth <= 768 ? 13 : 14 }}>{project.title}</Text>
                              {project.genre && (
                                <Tag color="blue" style={{ margin: 0, fontSize: window.innerWidth <= 768 ? 11 : 12 }}>{project.genre}</Tag>
                              )}
                              {getStatusTag(project.status)}
                            </div>
                            <Text type="secondary" style={{ fontSize: window.innerWidth <= 768 ? 11 : 12 }}>
                              {project.current_words || 0} 字
                              {project.description && ` · ${project.description.substring(0, window.innerWidth <= 768 ? 30 : 50)}${project.description.length > (window.innerWidth <= 768 ? 30 : 50) ? '...' : ''}`}
                            </Text>
                          </div>
                          {window.innerWidth > 768 && (
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {formatDate(project.updated_at)}
                            </Text>
                          )}
                        </div>
                      </Card>
                    ))}
                  </Space>
                )}
              </div>
            </div>

            {selectedProjectIds.length > 0 && (
              <Alert
                message={`已选择 ${selectedProjectIds.length} 个项目`}
                type="info"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Space>
        </Modal>

        {/* 编辑项目对话框 */}
        <Modal
          title={`编辑项目: ${editingProject?.title || ''}`}
          open={editModalVisible}
          onOk={handleUpdateProject}
          onCancel={handleCloseEditModal}
          confirmLoading={updating}
          okText="保存"
          cancelText="取消"
          width={window.innerWidth <= 768 ? '90%' : 600}
          centered
          styles={{
            body: {
              maxHeight: window.innerWidth <= 768 ? '60vh' : 'auto',
              overflowY: 'auto',
              padding: window.innerWidth <= 768 ? '16px' : '24px'
            }
          }}
        >
          <Form
            form={editForm}
            layout="vertical"
            autoComplete="off"
          >
            <Form.Item
              label="项目简介"
              name="description"
              rules={[
                { max: 1000, message: '简介不能超过1000字' }
              ]}
            >
              <Input.TextArea
                rows={4}
                placeholder="请输入项目简介（选填）"
                showCount
                maxLength={1000}
              />
            </Form.Item>

            <Form.Item
              label="目标字数"
              name="target_words"
              rules={[
                { type: 'number', min: 0, message: '目标字数不能为负数' },
                { type: 'number', max: 2147483647, message: '目标字数超出范围' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                placeholder="请输入目标字数（选填，最大21亿字）"
                min={0}
                max={2147483647}
                step={1000}
                addonAfter="字"
              />
            </Form.Item>
          </Form>
        </Modal>

        <ChangelogFloatingButton />
      </div>
    </div>
  );
}