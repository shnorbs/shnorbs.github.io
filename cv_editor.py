#!/usr/bin/env python3
"""
CV Template Editor CLI
A command-line tool to edit and manage your CV template.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import click

@dataclass
class ContactInfo:
    name: str = ""
    title: str = ""
    address: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""

@dataclass
class Education:
    degree: str = ""
    institution: str = ""
    location: str = ""
    duration: str = ""
    description: str = ""

@dataclass
class Experience:
    position: str = ""
    company: str = ""
    location: str = ""
    duration: str = ""
    description: str = ""

@dataclass
class Project:
    title: str = ""
    subtitle: str = ""
    technologies: str = ""
    description: str = ""
    links: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.links is None:
            self.links = []

@dataclass
class Award:
    title: str = ""
    description: str = ""

@dataclass
class Skills:
    programming_languages: List[str] = None
    frameworks: List[str] = None
    tools: List[str] = None

    def __post_init__(self):
        if self.programming_languages is None:
            self.programming_languages = []
        if self.frameworks is None:
            self.frameworks = []
        if self.tools is None:
            self.tools = []

class CVEditor:
    def __init__(self, html_file: str):
        self.html_file = Path(html_file)
        if not self.html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        self.soup = BeautifulSoup(self.content, 'html5lib')

    def save(self):
        """Save the modified HTML back to file"""
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(str(self.soup.prettify()))
        print(f"✅ CV updated successfully: {self.html_file}")

    def backup(self):
        """Create a backup of the original file"""
        backup_file = self.html_file.with_suffix('.html.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"📄 Backup created: {backup_file}")

    def update_contact_info(self, contact: ContactInfo):
        """Update contact information"""
        if contact.name:
            name_elem = self.soup.find('h1', class_='name', attrs={'content': 'true'})
            if name_elem:
                name_elem.string = contact.name

        if contact.title:
            title_elem = self.soup.find('p', class_='title', attrs={'content': 'true'})
            if title_elem:
                title_elem.string = contact.title

        # Update contact items
        contact_items = self.soup.find_all('div', class_='contact-item')
        
        for item in contact_items:
            span_text = item.find('span')
            if not span_text:
                continue
                
            icon = span_text.get_text().strip()
            
            if icon == '📍' and contact.address:
                editable = item.find('span', attrs={'content': 'true'})
                if editable:
                    editable.string = contact.address
                    
            elif icon == '📧' and contact.email:
                editable = item.find('a', attrs={'content': 'true'})
                if editable:
                    editable.string = contact.email
                    editable['href'] = f"mailto:{contact.email}"
                    
            elif icon == '📱' and contact.phone:
                editable = item.find('span', attrs={'content': 'true'})
                if editable:
                    editable.string = contact.phone
                    
            elif icon == '🔗' and contact.linkedin:
                editable = item.find('a', attrs={'content': 'true'})
                if editable:
                    editable.string = contact.linkedin
                    editable['href'] = contact.linkedin
                    
            elif icon == '💻' and contact.github:
                editable = item.find('a', attrs={'content': 'true'})
                if editable:
                    editable.string = contact.github
                    editable['href'] = contact.github

    def add_experience(self, experience: Experience):
        """Add a new experience entry"""
        experience_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Experience' in text.strip())
        if not experience_section_h2:
            print("⚠️ Warning: Experience section not found, skipping experience entry")
            return
            
        experience_section = experience_section_h2.parent
        
        # Create new experience item
        new_item = self.soup.new_tag('div', **{'class': 'experience-item'})
        
        # Header
        header = self.soup.new_tag('div', **{'class': 'item-header'})
        
        # Title info
        title_div = self.soup.new_tag('div')
        
        title_h3 = self.soup.new_tag('h3', **{'class': 'item-title', 'content': 'true'})
        title_h3.string = experience.position
        
        company_p = self.soup.new_tag('p', **{'class': 'item-company', 'content': 'true'})
        company_p.string = experience.company
        
        location_p = self.soup.new_tag('p', **{'class': 'item-location', 'content': 'true'})
        location_p.string = experience.location
        
        title_div.append(title_h3)
        title_div.append(company_p)
        title_div.append(location_p)
        
        # Duration
        duration_div = self.soup.new_tag('div', **{'class': 'item-duration', 'content': 'true'})
        duration_div.string = experience.duration
        
        header.append(title_div)
        header.append(duration_div)
        
        # Description
        description_p = self.soup.new_tag('p', **{'class': 'item-description', 'content': 'true'})
        description_p.string = experience.description
        
        new_item.append(header)
        new_item.append(description_p)
        
        # Insert at the beginning of experience section
        first_experience = experience_section.find('div', class_='experience-item')
        if first_experience:
            first_experience.insert_before(new_item)
        else:
            experience_section.append(new_item)

    def add_project(self, project: Project):
        """Add a new project entry"""
        projects_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Featured Projects' in text.strip())
        if not projects_section_h2:
            print("⚠️ Warning: Projects section not found, skipping project entry")
            return
            
        projects_section = projects_section_h2.parent
        
        # Create new project item
        new_item = self.soup.new_tag('div', **{'class': 'project-item'})
        
        # Header
        header = self.soup.new_tag('div', **{'class': 'item-header'})
        
        # Title info
        title_div = self.soup.new_tag('div')
        
        title_h3 = self.soup.new_tag('h3', **{'class': 'item-title', 'content': 'true'})
        title_h3.string = project.title
        
        subtitle_p = self.soup.new_tag('p', **{'class': 'item-company', 'content': 'true'})
        subtitle_p.string = project.subtitle
        
        title_div.append(title_h3)
        title_div.append(subtitle_p)
        
        # Technologies
        tech_div = self.soup.new_tag('div', **{'class': 'item-duration', 'content': 'true'})
        tech_div.string = project.technologies
        
        header.append(title_div)
        header.append(tech_div)
        
        # Description
        description_p = self.soup.new_tag('p', **{'class': 'item-description', 'content': 'true'})
        description_p.string = project.description
        
        new_item.append(header)
        new_item.append(description_p)
        
        # Links
        if project.links:
            links_div = self.soup.new_tag('div', **{'class': 'project-links'})
            for link in project.links:
                link_a = self.soup.new_tag('a', href=link.get('url', '#'), 
                                         **{'class': 'project-link', 'content': 'true'})
                link_a.string = link.get('text', '🔗 Link')
                links_div.append(link_a)
            new_item.append(links_div)
        
        # Insert at the beginning of projects section
        first_project = projects_section.find('div', class_='project-item')
        if first_project:
            first_project.insert_before(new_item)
        else:
            projects_section.append(new_item)

    def update_skills(self, skills: Skills):
        """Update skills section"""
        skills_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Skills' in text.strip())
        if not skills_section_h2:
            print("⚠️ Warning: Skills section not found, skipping skills update")
            return
            
        skills_section = skills_section_h2.parent
        skills_grid = skills_section.find('div', class_='skills-grid')
        
        if not skills_grid:
            return
            
        skill_categories = skills_grid.find_all('div', class_='skill-category')
        
        for category in skill_categories:
            h4 = category.find('h4')
            if not h4:
                continue
                
            category_name = h4.get_text().strip()
            skill_tags = category.find('div', class_='skill-tags')
            
            if category_name == "Programming Languages" and skills.programming_languages:
                skill_tags.clear()
                for skill in skills.programming_languages:
                    tag = self.soup.new_tag('span', **{'class': 'skill-tag', 'content': 'true'})
                    tag.string = skill
                    skill_tags.append(tag)
                    
            elif category_name == "Frameworks & Technologies" and skills.frameworks:
                skill_tags.clear()
                for skill in skills.frameworks:
                    tag = self.soup.new_tag('span', **{'class': 'skill-tag', 'content': 'true'})
                    tag.string = skill
                    skill_tags.append(tag)
                    
            elif category_name == "Tools & Platforms" and skills.tools:
                skill_tags.clear()
                for skill in skills.tools:
                    tag = self.soup.new_tag('span', **{'class': 'skill-tag', 'content': 'true'})
                    tag.string = skill
                    skill_tags.append(tag)

    def extract_data(self) -> Dict:
        """Extract current CV data to JSON format"""
        data = {}
        
        # Contact info
        name_elem = self.soup.find('h1', class_='name')
        title_elem = self.soup.find('p', class_='title')
        
        contact_info = {
            'name': name_elem.get_text().strip() if name_elem else "",
            'title': title_elem.get_text().strip() if title_elem else "",
        }
        
        # Extract contact details
        contact_items = self.soup.find_all('div', class_='contact-item')
        for item in contact_items:
            span_text = item.find('span')
            if not span_text:
                continue
                
            icon = span_text.get_text().strip()
            
            if icon == '📍':
                editable = item.find('span', class_='editable')
                if editable:
                    contact_info['address'] = editable.get_text().strip()
                    
            elif icon == '📧':
                editable = item.find('a', class_='editable')
                if editable:
                    contact_info['email'] = editable.get_text().strip()
                    
            elif icon == '📱':
                editable = item.find('span', class_='editable')
                if editable:
                    contact_info['phone'] = editable.get_text().strip()
                    
            elif icon == '🔗':
                editable = item.find('a', class_='editable')
                if editable:
                    contact_info['linkedin'] = editable.get('href', '')
                    
            elif icon == '💻':
                editable = item.find('a', class_='editable')
                if editable:
                    contact_info['github'] = editable.get('href', '')
        
        data['contact'] = contact_info
        
        # Experience
        data['experience'] = []
        experience_items = self.soup.find_all('div', class_='experience-item')
        for item in experience_items:
            exp = {}
            title_elem = item.find('h3', class_='item-title')
            company_elem = item.find('p', class_='item-company')
            location_elem = item.find('p', class_='item-location')
            duration_elem = item.find('div', class_='item-duration')
            description_elem = item.find('p', class_='item-description')
            
            if title_elem:
                exp['position'] = title_elem.get_text().strip()
            if company_elem:
                exp['company'] = company_elem.get_text().strip()
            if location_elem:
                exp['location'] = location_elem.get_text().strip()
            if duration_elem:
                exp['duration'] = duration_elem.get_text().strip()
            if description_elem:
                exp['description'] = description_elem.get_text().strip()
                
            data['experience'].append(exp)
        
        # Projects
        data['projects'] = []
        project_items = self.soup.find_all('div', class_='project-item')
        for item in project_items:
            proj = {}
            title_elem = item.find('h3', class_='item-title')
            subtitle_elem = item.find('p', class_='item-company')
            tech_elem = item.find('div', class_='item-duration')
            description_elem = item.find('p', class_='item-description')
            
            if title_elem:
                proj['title'] = title_elem.get_text().strip()
            if subtitle_elem:
                proj['subtitle'] = subtitle_elem.get_text().strip()
            if tech_elem:
                proj['technologies'] = tech_elem.get_text().strip()
            if description_elem:
                proj['description'] = description_elem.get_text().strip()
            
            # Extract project links
            links = []
            link_elements = item.find_all('a', class_='project-link')
            for link in link_elements:
                links.append({
                    'text': link.get_text().strip(),
                    'url': link.get('href', '')
                })
            proj['links'] = links
                
            data['projects'].append(proj)
        
        # Education
        data['education'] = []
        education_items = self.soup.find_all('div', class_='education-item')
        for item in education_items:
            edu = {}
            title_elem = item.find('h3', class_='item-title')
            institution_elem = item.find('p', class_='item-company')
            location_elem = item.find('p', class_='item-location')
            duration_elem = item.find('div', class_='item-duration')
            description_elem = item.find('p', class_='item-description')
            
            if title_elem:
                edu['degree'] = title_elem.get_text().strip()
            if institution_elem:
                edu['institution'] = institution_elem.get_text().strip()
            if location_elem:
                edu['location'] = location_elem.get_text().strip()
            if duration_elem:
                edu['duration'] = duration_elem.get_text().strip()
            if description_elem:
                edu['description'] = description_elem.get_text().strip()
                
            data['education'].append(edu)
        
        # Skills
        skills_data = {
            'programming_languages': [],
            'frameworks': [],
            'tools': []
        }
        
        skill_categories = self.soup.find_all('div', class_='skill-category')
        for category in skill_categories:
            h4 = category.find('h4')
            if not h4:
                continue
                
            category_name = h4.get_text().strip()
            skill_tags = category.find_all('span', class_='skill-tag')
            skills = [tag.get_text().strip() for tag in skill_tags]
            
            if category_name == "Programming Languages":
                skills_data['programming_languages'] = skills
            elif category_name == "Frameworks & Technologies":
                skills_data['frameworks'] = skills
            elif category_name == "Tools & Platforms":
                skills_data['tools'] = skills
        
        data['skills'] = skills_data
        
        # Awards
        data['awards'] = []
        award_items = self.soup.find_all('div', class_='awards-item')
        for item in award_items:
            award = {}
            title_elem = item.find('h3', class_='award-title')
            description_elem = item.find('p', class_='award-description')
            
            if title_elem:
                award['title'] = title_elem.get_text().strip()
            if description_elem:
                award['description'] = description_elem.get_text().strip()
                
            data['awards'].append(award)
        
        return data

    def import_data(self, json_data: Dict):
        """Import CV data from JSON format"""
        try:
            # Update contact information if provided
            if 'contact' in json_data:
                contact_data = json_data['contact']
                contact_info = ContactInfo(
                    name=contact_data.get('name', ''),
                    title=contact_data.get('title', ''),
                    email=contact_data.get('email', ''),
                    phone=contact_data.get('phone', ''),
                    address=contact_data.get('address', ''),
                    linkedin=contact_data.get('linkedin', ''),
                    github=contact_data.get('github', '')
                )
                self.update_contact_info(contact_info)
                print("✅ Contact information imported")

            # Import experience entries
            if 'experience' in json_data and json_data['experience']:
                experience_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Experience' in text.strip())
                if experience_section_h2:
                    experience_section = experience_section_h2.parent
                    # Clear existing experience first
                    existing_items = experience_section.find_all('div', class_='experience-item')
                    for item in existing_items:
                        item.decompose()
                    
                    # Add new experience entries
                    for exp_data in json_data['experience']:
                        experience = Experience(
                            position=exp_data.get('position', ''),
                            company=exp_data.get('company', ''),
                            location=exp_data.get('location', ''),
                            duration=exp_data.get('duration', ''),
                            description=exp_data.get('description', '')
                        )
                        self.add_experience(experience)
                    print(f"✅ {len(json_data['experience'])} experience entries imported")
                else:
                    print("⚠️ Warning: Experience section not found in HTML")

            # Import projects
            if 'projects' in json_data and json_data['projects']:
                projects_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Featured Projects' in text.strip())
                if projects_section_h2:
                    projects_section = projects_section_h2.parent
                    # Clear existing projects first
                    existing_items = projects_section.find_all('div', class_='project-item')
                    for item in existing_items:
                        item.decompose()
                    
                    # Add new project entries
                    for proj_data in json_data['projects']:
                        links = proj_data.get('links', [])
                        project = Project(
                            title=proj_data.get('title', ''),
                            subtitle=proj_data.get('subtitle', ''),
                            technologies=proj_data.get('technologies', ''),
                            description=proj_data.get('description', ''),
                            links=links
                        )
                        self.add_project(project)
                    print(f"✅ {len(json_data['projects'])} projects imported")
                else:
                    print("⚠️ Warning: Projects section not found in HTML")

            # Import skills
            if 'skills' in json_data:
                skills_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Skills' in text.strip())
                if skills_section_h2:
                    skills_data = json_data['skills']
                    skills = Skills(
                        programming_languages=skills_data.get('programming_languages', []),
                        frameworks=skills_data.get('frameworks', []),
                        tools=skills_data.get('tools', [])
                    )
                    self.update_skills(skills)
                    print("✅ Skills imported")
                else:
                    print("⚠️ Warning: Skills section not found in HTML")

            # Import education
            if 'education' in json_data and json_data['education']:
                education_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Education' in text.strip())
                if education_section_h2:
                    education_section = education_section_h2.parent
                    # Clear existing education first
                    existing_items = education_section.find_all('div', class_='education-item')
                    for item in existing_items:
                        item.decompose()
                    
                    # Add new education entries
                    for edu_data in json_data['education']:
                        self.add_education(Education(
                            degree=edu_data.get('degree', ''),
                            institution=edu_data.get('institution', ''),
                            location=edu_data.get('location', ''),
                            duration=edu_data.get('duration', ''),
                            description=edu_data.get('description', '')
                        ))
                    print(f"✅ {len(json_data['education'])} education entries imported")
                else:
                    print("⚠️ Warning: Education section not found in HTML")

            # Import awards
            if 'awards' in json_data and json_data['awards']:
                awards_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Awards' in text.strip() and 'Achievements' in text.strip())
                if awards_section_h2:
                    awards_section = awards_section_h2.parent
                    # Clear existing awards first
                    existing_items = awards_section.find_all('div', class_='awards-item')
                    for item in existing_items:
                        item.decompose()
                    
                    # Add new award entries
                    for award_data in json_data['awards']:
                        self.add_award(Award(
                            title=award_data.get('title', ''),
                            description=award_data.get('description', '')
                        ))
                    print(f"✅ {len(json_data['awards'])} awards imported")
                else:
                    print("⚠️ Warning: Awards section not found in HTML")

        except Exception as e:
            print(f"❌ Error importing data: {e}")
            raise

    def add_education(self, education: Education):
        """Add a new education entry"""
        education_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Education' in text.strip())
        if not education_section_h2:
            print("⚠️ Warning: Education section not found, skipping education entry")
            return
            
        education_section = education_section_h2.parent
        
        # Create new education item
        new_item = self.soup.new_tag('div', **{'class': 'education-item'})
        
        # Header
        header = self.soup.new_tag('div', **{'class': 'item-header'})
        
        # Title info
        title_div = self.soup.new_tag('div')
        
        title_h3 = self.soup.new_tag('h3', **{'class': 'item-title', 'content': 'true'})
        title_h3.string = education.degree
        
        institution_p = self.soup.new_tag('p', **{'class': 'item-company', 'content': 'true'})
        institution_p.string = education.institution
        
        location_p = self.soup.new_tag('p', **{'class': 'item-location', 'content': 'true'})
        location_p.string = education.location
        
        title_div.append(title_h3)
        title_div.append(institution_p)
        title_div.append(location_p)
        
        # Duration
        duration_div = self.soup.new_tag('div', **{'class': 'item-duration', 'content': 'true'})
        duration_div.string = education.duration
        
        header.append(title_div)
        header.append(duration_div)
        
        # Description
        description_p = self.soup.new_tag('p', **{'class': 'item-description', 'content': 'true'})
        description_p.string = education.description
        
        new_item.append(header)
        new_item.append(description_p)
        
        # Insert at the beginning of education section
        first_education = education_section.find('div', class_='education-item')
        if first_education:
            first_education.insert_before(new_item)
        else:
            education_section.append(new_item)

    def add_award(self, award: Award):
        """Add a new award entry"""
        awards_section_h2 = self.soup.find('h2', class_='section-title', string=lambda text: text and 'Awards' in text.strip() and 'Achievements' in text.strip())
        if not awards_section_h2:
            print("⚠️ Warning: Awards section not found, skipping award entry")
            return
            
        awards_section = awards_section_h2.parent
        
        # Create new award item
        new_item = self.soup.new_tag('div', **{'class': 'awards-item'})
        
        title_h3 = self.soup.new_tag('h3', **{'class': 'award-title', 'content': 'true'})
        title_h3.string = award.title
        
        description_p = self.soup.new_tag('p', **{'class': 'award-description', 'content': 'true'})
        description_p.string = award.description
        
        new_item.append(title_h3)
        new_item.append(description_p)
        
        # Insert at the beginning of awards section
        first_award = awards_section.find('div', class_='awards-item')
        if first_award:
            first_award.insert_before(new_item)
        else:
            awards_section.append(new_item)

@click.group()
def cli():
    """CV Template Editor - A CLI tool to import CV data from JSON"""
    pass

@click.command()
@click.option('--input', required=True, help='JSON file to import from')
@click.option('--file', default='index.html', help='HTML file to edit')
def import_data(input, file):
    """Import CV data from JSON format"""
    try:
        editor = CVEditor(file)
        editor.backup()
        
        # Load JSON data
        with open(input, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        editor.import_data(json_data)
        editor.save()
        
        click.echo(f"✅ CV data imported successfully from: {input}")
        
    except FileNotFoundError:
        click.echo(f"❌ Error: JSON file not found: {input}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON format: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

# Add commands to the CLI group
cli.add_command(import_data)

if __name__ == '__main__':
    cli()
