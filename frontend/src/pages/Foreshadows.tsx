import { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Modal, Form, Input, Select, 
  InputNumber, Tag, Space, message, Popconfirm, Badge,
  Tooltip, Progress, Switch, Timeline, Statistic, Row, Col
} from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, 
  CheckCircleOutlined, ExclamationCircleOutlined,
  BulbOutlined, EyeOutlined, ClockCircleOutlined
} from '@ant-design/icons';
import { useStore } from '../store';
import type { 
  Foreshadow, ForeshadowListResponse, 
  ForeshadowReminder 
} from '../types';
import axios from 'axios';

const { TextArea } = Input;

const FORESHADOW_TYPES = [
  { value: 'character', label: '角色相关', color: 'blue' },
  { value: 'plot', label: '情节相关', color: 'green' },
  { value: 'item', label: '物品相关', color: 'orange' },
  { value: 'setting', label: '设定相关', color: 'purple' },
  { value: 'relationship', label: '关系相关', color: 'cyan' },
];

const STATUS_CONFIG = {
  planted: { label: '已埋设', color: 'processing', icon: <BulbOutlined /> },
  hinted: { label: '已暗示', color: 'warning', icon: <EyeOutlined /> },
  resolved: { label: '已回收', color: 'success', icon: <CheckCircleOutlined /> },
  abandoned: { label: '已放弃', color: 'default', icon: <ClockCircleOutlined /> },
};

export default function Foreshadows() {
  const { currentProject, chapters } = useStore();
  const [foreshadows, setForeshadows] = useState<Foreshadow[]>([]);
  const [reminders, setReminders] = useState<ForeshadowReminder[]>([]);
  const [stats, setStats] = useState({ planted: 0, resolved: 0, pending: 0 });
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [resolveModalVisible, setResolveModalVisible] = useState(false);
  const [editingForeshadow, setEditingForeshadow] = useState<Foreshadow | null>(null);
  const [resolvingForeshadow, setResolvingForeshadow] = useState<Foreshadow | null>(null);
  const [form] = Form.useForm();
  const [resolveForm] = Form.useForm();

  const currentChapter = chapters.length > 0 
    ? Math.max(...chapters.map(c => c.chapter_number)) 
    : 1;

  useEffect(() => {
    if (currentProject?.id) {
      fetchForeshadows();
      fetchReminders();
    }
  }, [currentProject?.id]);

  const fetchForeshadows = async () => {
    if (!currentProject?.id) return;
    setLoading(true);
    try {
      const response = await axios.get<ForeshadowListResponse>(
        `/api/foreshadows?project_id=${currentProject.id}`
      );
      setForeshadows(response.data.items);
      setStats({
        planted: response.data.planted_count || 0,
        resolved: response.data.resolved_count || 0,
        pending: response.data.pending_count || 0,
      });
    } catch (error) {
      message.error('获取伏笔列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchReminders = async () => {
    if (!currentProject?.id) return;
    try {
      const response = await axios.get(
        `/api/foreshadows/reminders?project_id=${currentProject.id}&current_chapter=${currentChapter}`
      );
      setReminders(response.data.reminders);
    } catch (error) {
      console.error('获取提醒失败:', error);
    }
  };

  const handleCreate = () => {
    setEditingForeshadow(null);
    form.resetFields();
    form.setFieldsValue({
      foreshadow_type: 'plot',
      importance: 5,
      remind_before_chapters: 5,
      auto_remind: true,
    });
    setModalVisible(true);
  };

  const handleEdit = (record: Foreshadow) => {
    setEditingForeshadow(record);
    form.setFieldsValue({
      ...record,
      auto_remind: record.auto_remind,
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingForeshadow) {
        await axios.put(`/api/foreshadows/${editingForeshadow.id}`, values);
        message.success('更新成功');
      } else {
        await axios.post('/api/foreshadows', {
          ...values,
          project_id: currentProject?.id,
        });
        message.success('创建成功');
      }
      
      setModalVisible(false);
      fetchForeshadows();
      fetchReminders();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`/api/foreshadows/${id}`);
      message.success('删除成功');
      fetchForeshadows();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleResolve = (record: Foreshadow) => {
    setResolvingForeshadow(record);
    resolveForm.resetFields();
    resolveForm.setFieldsValue({
      resolved_chapter_number: currentChapter,
    });
    setResolveModalVisible(true);
  };

  const handleResolveSubmit = async () => {
    if (!resolvingForeshadow) return;
    try {
      const values = await resolveForm.validateFields();
      await axios.post(`/api/foreshadows/${resolvingForeshadow.id}/resolve`, values);
      message.success('伏笔已回收');
      setResolveModalVisible(false);
      fetchForeshadows();
      fetchReminders();
    } catch (error) {
      message.error('回收失败');
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      render: (text: string, record: Foreshadow) => (
        <Space>
          <span>{text}</span>
          {record.importance >= 8 && <Tag color="red">重要</Tag>}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'foreshadow_type',
      key: 'foreshadow_type',
      width: 100,
      render: (type: string) => {
        const config = FORESHADOW_TYPES.find(t => t.value === type);
        return <Tag color={config?.color}>{config?.label || type}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: keyof typeof STATUS_CONFIG) => {
        const config = STATUS_CONFIG[status];
        return (
          <Badge status={config.color as any} text={config.label} />
        );
      },
    },
    {
      title: '重要度',
      dataIndex: 'importance',
      key: 'importance',
      width: 120,
      render: (value: number) => (
        <Progress 
          percent={value * 10} 
          size="small" 
          format={() => `${value}/10`}
          strokeColor={value >= 8 ? '#ff4d4f' : value >= 5 ? '#faad14' : '#52c41a'}
        />
      ),
    },
    {
      title: '埋设章节',
      dataIndex: 'planted_chapter_number',
      key: 'planted_chapter_number',
      width: 100,
      render: (num: number) => num ? `第${num}章` : '-',
    },
    {
      title: '预期回收',
      dataIndex: 'resolved_chapter_number',
      key: 'resolved_chapter_number',
      width: 100,
      render: (num: number, record: Foreshadow) => {
        if (record.status === 'resolved') {
          return <Tag color="green">第{num}章</Tag>;
        }
        if (num && num <= currentChapter) {
          return <Tag color="red">第{num}章 (已过期)</Tag>;
        }
        return num ? `第${num}章` : '-';
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: Foreshadow) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          {record.status !== 'resolved' && (
            <Tooltip title="回收伏笔">
              <Button 
                type="text" 
                icon={<CheckCircleOutlined />}
                style={{ color: '#52c41a' }}
                onClick={() => handleResolve(record)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确定删除此伏笔？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (!currentProject) {
    return <Card>请先选择一个项目</Card>;
  }

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已埋设" 
              value={stats.planted} 
              prefix={<BulbOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已回收" 
              value={stats.resolved} 
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待回收" 
              value={stats.pending} 
              prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="当前章节" 
              value={currentChapter} 
              suffix="章"
            />
          </Card>
        </Col>
      </Row>

      {/* 提醒区域 */}
      {reminders.length > 0 && (
        <Card 
          title={<><ExclamationCircleOutlined style={{ color: '#faad14' }} /> 伏笔提醒</>}
          style={{ marginBottom: 24 }}
          size="small"
        >
          <Timeline>
            {reminders.slice(0, 5).map(r => (
              <Timeline.Item 
                key={r.foreshadow_id}
                color={r.chapters_remaining <= 0 ? 'red' : r.chapters_remaining <= 3 ? 'orange' : 'blue'}
              >
                <strong>{r.title}</strong>
                <span style={{ marginLeft: 8, color: '#999' }}>
                  {r.chapters_remaining <= 0 
                    ? '已过期！' 
                    : `还剩 ${r.chapters_remaining} 章`}
                </span>
                <div style={{ color: '#666', fontSize: 12 }}>
                  预期在第 {r.expected_resolve_chapter} 章回收
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}

      {/* 伏笔列表 */}
      <Card 
        title="伏笔管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建伏笔
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={foreshadows}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          expandable={{
            expandedRowRender: (record) => (
              <div style={{ padding: '12px 0' }}>
                <p><strong>描述：</strong>{record.description}</p>
                {record.planted_content && (
                  <p><strong>埋设原文：</strong>{record.planted_content}</p>
                )}
                {record.resolved_content && (
                  <p><strong>回收原文：</strong>{record.resolved_content}</p>
                )}
                {record.notes && (
                  <p><strong>备注：</strong>{record.notes}</p>
                )}
                {record.tags && record.tags.length > 0 && (
                  <p>
                    <strong>标签：</strong>
                    {record.tags.map((tag: string) => <Tag key={tag}>{tag}</Tag>)}
                  </p>
                )}
              </div>
            ),
          }}
        />
      </Card>

      {/* 创建/编辑弹窗 */}
      <Modal
        title={editingForeshadow ? '编辑伏笔' : '新建伏笔'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="简短描述这个伏笔" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="详细描述"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <TextArea rows={3} placeholder="详细描述伏笔内容和预期效果" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="foreshadow_type" label="类型">
                <Select options={FORESHADOW_TYPES} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="importance" label="重要度">
                <InputNumber min={1} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="planted_chapter_number" label="埋设章节">
                <InputNumber min={1} style={{ width: '100%' }} placeholder="第几章埋设" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="resolved_chapter_number" label="预期回收章节">
                <InputNumber min={1} style={{ width: '100%' }} placeholder="预计第几章回收" />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="planted_content" label="埋设原文">
            <TextArea rows={2} placeholder="摘录埋设伏笔的原文" />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="remind_before_chapters" label="提前提醒章数">
                <InputNumber min={1} max={50} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="auto_remind" label="自动提醒" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item name="notes" label="备注">
            <TextArea rows={2} placeholder="作者备注" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 回收弹窗 */}
      <Modal
        title="回收伏笔"
        open={resolveModalVisible}
        onOk={handleResolveSubmit}
        onCancel={() => setResolveModalVisible(false)}
      >
        <Form form={resolveForm} layout="vertical">
          <Form.Item
            name="resolved_chapter_number"
            label="回收章节"
            rules={[{ required: true, message: '请输入章节号' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item name="resolved_content" label="回收原文">
            <TextArea rows={3} placeholder="摘录回收伏笔的原文" />
          </Form.Item>
          
          <Form.Item name="notes" label="备注">
            <TextArea rows={2} placeholder="回收备注" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
