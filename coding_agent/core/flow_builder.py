from base_nodes import Flow

from coding_agent.logger import setup_logger
from coding_agent.nodes.decision_nodes import MainDecisionAgent
from coding_agent.nodes.edit_nodes import ReadTargetFileNode, \
    AnalyzeAndPlanNode, ApplyChangesNode
from coding_agent.nodes.file_nodes import ReadFileAction, GrepSearchAction, \
    ListDirAction, DeleteFileAction
from coding_agent.nodes.response_nodes import FormatResponseNode

# Configure logging
logger = setup_logger("coding_agent")


def create_edit_agent() -> Flow:
    # Create nodes
    read_target = ReadTargetFileNode()
    analyze_plan = AnalyzeAndPlanNode()
    apply_changes = ApplyChangesNode()

    # Connect nodes using default action (no named actions)
    read_target >> analyze_plan
    analyze_plan >> apply_changes

    # Create flow
    return Flow(start=read_target)


def create_main_flow() -> Flow:
    # Create nodes
    main_agent = MainDecisionAgent()
    read_action = ReadFileAction()
    grep_action = GrepSearchAction()
    list_dir_action = ListDirAction()
    delete_action = DeleteFileAction()
    edit_agent = create_edit_agent()
    format_response = FormatResponseNode()

    # Connect main agent to action nodes
    main_agent - "read_file" >> read_action
    main_agent - "grep_search" >> grep_action
    main_agent - "list_dir" >> list_dir_action
    main_agent - "delete_file" >> delete_action
    main_agent - "edit_file" >> edit_agent
    main_agent - "finish" >> format_response

    # Connect action nodes back to main agent using default action
    read_action >> main_agent
    grep_action >> main_agent
    list_dir_action >> main_agent
    delete_action >> main_agent
    edit_agent >> main_agent

    # Create flow
    return Flow(start=main_agent)


# Create the main flow
coding_agent_flow = create_main_flow()